class Pub:
    def __init__(self):
        self.crew_cost = 100

    def visit(self, character):
        print("\n=== Welcome to the Pub ===")
        if character.ship is None:
            print("You need a ship before you can recruit crew!")
            return

        print(f"Crew members available for {self.crew_cost} gold each")
        print(f"Your ship can hold {character.ship.crew_capacity} crew members")
        print(f"Current crew: {character.ship.current_crew}")

        amount = input("How many crew members would you like to recruit? ")
        try:
            amount = int(amount)
            total_cost = amount * self.crew_cost
            if (amount + character.ship.current_crew <= character.ship.crew_capacity and 
                character.gold >= total_cost):
                character.gold -= total_cost
                character.ship.current_crew += amount
                print(f"You hired {amount} new crew members!")
            else:
                print("You either can't afford this many crew members or your ship is too small!")
        except ValueError:
            print("Please enter a valid number!") 