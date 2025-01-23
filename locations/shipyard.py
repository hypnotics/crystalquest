from crystalquest.items import ship_types
from crystalquest.ships import Ship

class Shipyard:
    def __init__(self):
        self.ships = ship_types
        self.repair_cost = 200

    def visit(self, character):
        print("\n=== Welcome to the Shipyard ===")
        if character.ship:
            print(f"1. Buy new ship")
            print(f"2. Repair current ship (Hull: {character.ship.hull_current}/{character.ship.hull_max}, Cost: {self.repair_cost} gold)")
            print("3. Leave")
            
            choice = input("\nWhat would you like to do? ")
            
            if choice == "2":
                if character.ship.hull_current >= character.ship.hull_max:
                    print("Your ship is already fully repaired!")
                    return
                if character.gold >= self.repair_cost:
                    character.gold -= self.repair_cost
                    character.ship.hull_current = character.ship.hull_max
                    print("Ship fully repaired!")
                else:
                    print("You can't afford repairs!")
                return
            elif choice == "3":
                return

        print("\nAvailable ships:")
        for ship_name, stats in self.ships.items():
            print(f"{ship_name}: {stats['price']} gold (Crew: {stats['crew_max']}, "
                  f"Speed: {stats['speed']} squares/day, Hull: {stats['hull_max']}, "
                  f"Cargo: {stats['cargo']} barrels)")
        
        choice = input("\nWhat would you like to buy? (Enter ship name or 'no'): ").title()
        if choice in self.ships:
            if character.gold >= self.ships[choice]['price']:
                character.gold -= self.ships[choice]['price']
                character.ship = Ship(
                    choice, 
                    self.ships[choice]['price'],
                    self.ships[choice]['crew_max'],
                    self.ships[choice]['speed']
                )
                print(f"You bought a {choice}!")
            else:
                print("You can't afford this ship!") 