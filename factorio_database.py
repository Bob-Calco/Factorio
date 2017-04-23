import sqlite3
import factorio_orm as orm


# Database querying and data organizing
class Database:
    def __init__(self):
        print('Open database')
        self.conn = sqlite3.connect('Factorio_data.sqlite')
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()

    def close(self):
        print("Closing database")
        self.conn.close()

    # get a product and its ingredients. Input the item (name or pk) and the amount of machines building the product
    def search(self, item, value, is_machines_used, is_items_per_second):
        print('Search in database')
        product_data = self.__get_product(item)[0]
        product = orm.Item(product_data['id'], product_data['name'], product_data['buildtime'], product_data['buildamount'], product_data['machine_type'], is_machines_used, is_items_per_second, value)

        ingredients_data = self.__get_ingredients(product.pk)
        ingredients = []
        for row in ingredients_data:
            ingredients.append(orm.Item(row['id'], row['name'], row['buildtime'], row['buildamount'], row['machine_type'], amount_needed=row['amount']))

        product.ingredients = ingredients

        return product

    def get_all_machines(self):
        print('Finding all machines and their types')
        type_data = self.__get_machine_types()

        machines = {}
        for row in type_data:
            machines[row[1]] = []
        for row in type_data:
            machines_data = self.__get_machines(row[0])
            for machine in machines_data:
                if machine[1] == 5:
                    machines[row[1]].append(orm.Machine(machine[0], row[1], machine[2], machine[4], machine[5], mining_power=machine[6], mining_speed=machine[7]))
                else:
                    machines[row[1]].append(orm.Machine(machine[0], row[1],machine[2], machine[4], machine[5], crafting_speed=machine[3]))
        return machines

    def get_machine(self, name):
        print('Get ' + str(name) + ' from database')
        self.c.execute("SELECT id, type, name, crafting_speed, energy_consumption, electricity, mining_power, Mining_speed FROM machines WHERE name = '" + str(name) + "'")
        machine_data = self.c.fetchall()[0]
        machine = orm.Machine(machine_data['id'], machine_data['type'], machine_data['name'], machine_data['energy_consumption'], machine_data['electricity'], machine_data['crafting_speed'], machine_data['mining_power'], machine_data['Mining_speed'])
        return machine

    def __get_product(self, query):
        print('Get ' + str(query) + ' from database')
        try:
            int(query)
            self.c.execute("SELECT items.id, items.name, items.buildtime, items.buildamount, machine_types.name as machine_type "
                           "FROM items JOIN machine_types ON items.machine_type = machine_types.id WHERE items.id = " + str(query))
        except ValueError:
            self.c.execute("SELECT items.id, items.name, items.buildtime, items.buildamount, machine_types.name as machine_type "
                           "FROM items JOIN machine_types ON items.machine_type = machine_types.id WHERE items.name = '" + query + "'")
        return self.c.fetchall()

    def __get_ingredients(self, pk):
        print('Get ingredients from database')
        self.c.execute(
            "SELECT items.id, items.name, buildtime, buildamount, machine_types.name as machine_type, amount "
            "FROM ingredients "
            "JOIN items ON ingredients.ingredient = items.id "
            "JOIN machine_types ON items.machine_type = machine_types.id "
            "WHERE product = " + str(pk))
        return self.c.fetchall()

    def __get_machine_types(self):
        print('Getting all machine types from database')
        self.c.execute("SELECT * FROM machine_types")
        return self.c.fetchall()

    def __get_machines(self, machine_type):
        print('Getting machines from type from database')
        self.c.execute("SELECT * FROM machines WHERE type = " + str(machine_type))
        return self.c.fetchall()