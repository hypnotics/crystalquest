from crystalquest.prompts import ask_positive_int

class Pub:
    def __init__(self):
        self.crew_cost = 100

    def visit(self, character):
        print("\n=== Welcome to the Pub ===")
        if character.ship is None:
            print("You need a ship before you can recruit crew!")
            return

        capacity = getattr(character.ship, 'crew_capacity', None)
        current = getattr(character.ship, 'current_crew', 0)
        if capacity is None:
            print("This ship cannot take on crew.")
            return

        print(f"Crew members available for {self.crew_cost} gold each")
        print(f"Your ship can hold {capacity} crew members")
        print(f"Current crew: {current}")

        amount = ask_positive_int("How many crew members would you like to recruit? ")
        if amount is None:
            return

        total_cost = amount * self.crew_cost
        if amount + current <= capacity and character.gold >= total_cost:
            character.gold -= total_cost
            character.ship.current_crew = current + amount
            print(f"You hired {amount} new crew members!")
        else:
            print("You either can't afford this many crew members or your ship is too small!")
