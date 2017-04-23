import tkinter as tk
import functools
import factorio_database as fdb


# all the GUI stuff
class App(tk.Frame):
    def __init__(self, parent):
        print('Initialize app')
        # GUI initializing stuff
        tk.Frame.__init__(self, parent, bg="white", padx=30, pady=30)
        self.parent = parent

        # Title of the window
        self.parent.title("Factorio ratio calculator")
        self.pack()

        # Title on the frame
        self.title = tk.Label(self, text="Factorio ratios", bg="white", font="Sans-serif 27 bold")
        self.title.grid(row=0, columnspan=2)

        # Search field, button and interpretation
        self.search_frame = tk.Frame(self, bg="white", relief="groove", borderwidth=3, pady=10, padx=10)
        self.search_entry = tk.Entry(self.search_frame, font="sans-serif 13")
        self.search_entry.grid(row=0, column=1)

        self.search_button = tk.Button(self.search_frame, text="Query", font="sans-serif 13", command=self.process_query)
        self.search_button.grid(row=0, column=2)

        self.item_label_text = tk.StringVar()
        self.item_label_text.set('Enter a search query')
        self.item_label = tk.Label(self.search_frame, textvariable=self.item_label_text, bg="white", font="Sans-serif, 13")
        self.item_label.grid(row=2, column=1)

        self.search_frame.grid(row=1, column=1, sticky="W")

        # Frame to select the machine the calculations use
        self.machines_frame = MachineFrame(self)
        self.machines_frame.grid(row=3, column=0, sticky="N")

        # Frame for the main table
        self.product_frame = tk.Frame(self)

    # Function used when closing the app
    def close(self):
        print('Close app')
        self.parent.destroy()

    def process_query(self):
        print('Interpreting search query')
        query = self.search_entry.get()

        if "/s" in query:           # An items per second query
            index = query.find("/s")
            items_per_second = int(query[:index])
            item = query[index + 2:].strip()
            self.search(item, items_per_second, False, True)

        else:                       # An items per second query
            machines_used = None
            item = None
            for index, c in enumerate(query):
                if not c.isdigit():
                    machines_used = query[:index]
                    item = query[index:].strip()
                    break
            if machines_used == '':  # Not an amount of machines put in? Then we just use 1 machine
                machines_used = '1'
            machines_used = int(machines_used)
            self.search(item, machines_used, True, False)

    # Function bound to search button
    def search(self, item, value, is_machines_used, is_items_per_second):
        print('Search from app')
        # TODO: check whether the item is a valid item in the database
        # TODO: offer option to add it to the database, might require cascading to add ingredients and stuff

        # Get data from the database
        db = fdb.Database()
        product = db.search(item, value, is_machines_used, is_items_per_second)
        db.close()

        # Update the GUI
        if is_machines_used:
            self.item_label_text.set(str(value) + ' machines crafting ' + item)
        if is_items_per_second:
            self.item_label_text.set(str(value) + ' ' + item + ' per second')

        # Create a frame to hold the table with all the information on the item
        self.product_frame.destroy()  # TODO: store this frame so we can go back to it
        self.product_frame = ItemFrame(self, product, self.machines_frame.selected_machine_types)
        self.product_frame.grid(row=3, column=1, sticky="WN")
        # TODO: add a button to expand all the way down and stack up all similar ingredients


# Frame to show, expand and stuff for an item
class ItemFrame(tk.Frame):
    def __init__(self, parent, product, selected_machines):
        print('Initialize ItemFrame ' + product.name)
        tk.Frame.__init__(self, parent, bg="white", relief='groove', borderwidth=3, padx=5, pady=5)

        self.parent = parent
        self.table = {}
        self.product = product
        self.selected_machines = selected_machines

        self.table_header_name_frame = tk.Frame(self, bg="lightblue")
        self.table_header_name = tk.Label(self.table_header_name_frame, text="name", bg="lightblue")
        self.table_header_name.pack(side='left')
        self.table_header_name_frame.grid(row=0, column=0, sticky="EW")

        self.table_header_machines_frame = tk.Frame(self, bg="lightblue")
        self.table_header_machines = tk.Label(self.table_header_machines_frame, text="machines", bg="lightblue")
        self.table_header_machines.pack(side='left')
        self.table_header_machines_frame.grid(row=0, column=1, sticky="EW")

        self.table_header_ips_frame = tk.Frame(self, bg="lightblue")
        self.table_header_ips = tk.Label(self.table_header_ips_frame, text="items/s", bg="lightblue")
        self.table_header_ips.pack(side='left')
        self.table_header_ips_frame.grid(row=0, column=2, sticky="EW")

        for index, ingredient in enumerate(self.product.ingredients, start=1):

            name = tk.Label(self, text=ingredient.name, bg="white")
            name.grid(row=index, column=0, sticky="WN")
            self.table[(ingredient.pk, 'name')] = name

            ratio = self.product.ratio(ingredient, self.selected_machines[ingredient.machine_type].get(), self.selected_machines[self.product.machine_type].get())
            machines_needed = ratio[0]
            machines = tk.Label(self, text=machines_needed, bg="white")
            machines.grid(row=index, column=1, sticky="WN")
            self.table[(ingredient.pk, 'machines')] = machines

            items_per_second = ratio[1]
            itemsps = tk.Label(self,text=items_per_second, bg="white")
            itemsps.grid(row=index, column=2, sticky="WN")
            self.table[(ingredient.pk, 'items/s')] = itemsps

            expand_button = ExpandButton(self, ingredient, index)
            expand_button.grid(row=index, column=3, sticky="WN")
            self.table[(ingredient.pk, 'expand')] = expand_button

    def expand(self, ingredient, index):
        print('Expand ' + ingredient.name)
        db = fdb.Database()
        machines_needed = self.product.ratio(ingredient, self.selected_machines[ingredient.machine_type].get(), self.selected_machines[self.product.machine_type].get())[0]
        product = db.search(ingredient.pk, machines_needed, True, False)
        db.close()

        expanded_frame = ItemFrame(self, product, self.selected_machines)
        expanded_frame.grid(row=index, column=4, sticky="WN")
        self.table[(ingredient.pk, 'expanded frame')] = expanded_frame

    def collapse(self, ingredient):
        print('Collapse ' + ingredient.name)
        self.table[(ingredient.pk, 'expanded frame')].destroy()


class ExpandButton(tk.Button):
    def __init__(self, parent, ingredient, index):
        tk.Button.__init__(self, parent, bg="white", text="Expand", command=self.change)
        self.collapsed = True
        self.ingredient = ingredient
        self.index = index
        self.parent = parent

    def change(self):
        if self.collapsed:
            self.collapsed = False
            self.parent.expand(self.ingredient, self.index)
            self['text'] = 'Collapse'
        else:
            self.collapsed = True
            self.parent.collapse(self.ingredient)
            self['text'] = 'Expand'


class MachineFrame(tk.Frame):
    def __init__(self, parent):
        print('Initializing MachineFrame')
        tk.Frame.__init__(self, parent, bg="white", relief="groove", borderwidth=3, padx=10, pady=10)
        self.parent = parent

        self.title_label = tk.Label(self, text='Machines', bg="white", font="Sans-serif 18 bold")
        self.title_label.grid(row=0, column=0)

        db = fdb.Database()
        machines = db.get_all_machines()
        db.close()

        self.selected_machine_types = {}

        i = 1
        for machine_type in machines:
            tk.Label(self, text=machine_type, bg="white", font="Sans-serif 13 italic").grid(row=i*2-1, column=0)
            self.selected_machine_types[machine_type] = tk.StringVar(self)
            self.selected_machine_types[machine_type].set("Select a machine")
            list_of_machines = []
            for machine in machines[machine_type]:
                list_of_machines.append(machine.name)

            drop_down = tk.OptionMenu(self, self.selected_machine_types[machine_type], *list_of_machines)
            drop_down.grid(row=i*2, column=0)
            i += 1

# start doing things
root = tk.Tk()
app = App(root)
root.protocol("WM_DELETE_WINDOW", app.close)
root.mainloop()
