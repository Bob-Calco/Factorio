import factorio_database as fdb


# ORM
class Item:
    def __init__(self, pk, name, build_time, build_amount, machine_type, is_machines_used=None, is_items_per_second=None, value=None, amount_needed=None):
        print('Initialize ' + name)
        self.pk = pk
        self.name = name
        self.build_time = float(build_time)
        self.build_amount = float(build_amount)
        self.machine_type = machine_type

        # As an ingredient:
        if amount_needed is not None:
            self.amount_needed = int(amount_needed)
        # As a product:
        else:
            self.ingredients = []
            self.is_machines_used = is_machines_used
            self.is_items_per_second = is_items_per_second
            self.value = float(value)

    # this function runs from the instance of the product
    def ratio(self, ingredient, ingredient_machine, product_machine):
        print('Get machines needed of ' + ingredient.name)
        db = fdb.Database()
        product_machine = db.get_machine(product_machine)
        ingredient_machine = db.get_machine(ingredient_machine)
        machines_needed = 0.0
        ingredient_items_per_second = 0.0
        if self.is_machines_used:  # if we don't have the desired items/second for the product, calculate that first
            items_per_second = self.value * (1/(self.build_time / product_machine.crafting_speed)) * self.build_amount
        else:
            items_per_second = self.value

        if ingredient.machine_type == 'Assembling Machine' or ingredient.machine_type == 'Chemical Plant' or ingredient.machine_type == 'Furnace':
            one_ingredient_machine_items_per_second = (1/(ingredient.build_time / ingredient_machine.crafting_speed)) * ingredient.build_amount
            ingredient_items_per_second = items_per_second * ingredient.amount_needed
            machines_needed = ingredient_items_per_second / one_ingredient_machine_items_per_second

        elif ingredient.machine_type == 'Oil Refinery':
            pass

        elif ingredient.machine_type == 'Drill':
            one_ingredient_machine_items_per_second = (ingredient_machine.mining_power - 0.9) * ingredient_machine.mining_speed / 2  # TODO: change 0.9 to be 0.4 if it is about stone
            ingredient_items_per_second = items_per_second * ingredient.amount_needed
            machines_needed = ingredient_items_per_second / one_ingredient_machine_items_per_second

        db.close()
        return ['%.1f' % round(machines_needed, 1), '%.1f' % round(ingredient_items_per_second, 1)]


class Machine:
    def __init__(self, pk, machine_type, name, energy_consumption, is_electric, crafting_speed=None, mining_power=None, mining_speed=None):
        print('Initialize ' + name)
        self.pk = pk
        self.machine_type = machine_type
        self.name = name
        self.energy_consumption = energy_consumption
        self.is_electric = is_electric
        if crafting_speed:
            self.crafting_speed = crafting_speed
        if mining_power:
            self.mining_power = mining_power
        if mining_speed:
            self.mining_speed = mining_speed
