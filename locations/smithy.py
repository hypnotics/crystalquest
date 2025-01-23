from crystalquest.items import weapons

class Smithy:
    def __init__(self):
        self.weapons = weapons

    def visit(self, character):
        print("\n=== Welcome to the Smithy ===")
        print("Available weapons:")
        
        # Filter weapons based on whether player has a ship
        available_weapons = {}
        for name, stats in self.weapons.items():
            if stats.get('type') == 'ship':
                if character.ship:  # Only show ship weapons if player has a ship
                    available_weapons[name] = stats
            else:  # Always show personal weapons
                available_weapons[name] = stats

        # Display available weapons
        for weapon, stats in available_weapons.items():
            if stats['type'] == 'ship':
                print(f"{weapon}: {stats['price']} gold (Damage: {stats['damage']}, "
                      f"Cargo Space: {stats['cargo_space']}, {stats['description']})")
            else:
                print(f"{weapon}: {stats['price']} gold (Damage: {stats['damage']}, "
                      f"Type: {stats['type']})")

        choice = input("\nWhat would you like to buy? (Enter weapon name or 'no'): ").title()
        if choice in available_weapons:
            weapon_stats = available_weapons[choice]
            
            # Check cargo space for ship weapons
            if weapon_stats['type'] == 'ship':
                current_cargo = sum(item.get('cargo_space', 1) for item in character.inventory.values())
                if current_cargo + weapon_stats['cargo_space'] > character.ship.cargo_capacity:
                    print("Not enough cargo space on your ship!")
                    return

            if character.gold >= weapon_stats['price']:
                character.gold -= weapon_stats['price']
                if weapon_stats['type'] == 'ship':
                    character.ship.weapons = character.ship.weapons if hasattr(character.ship, 'weapons') else {}
                    character.ship.weapons[choice] = character.ship.weapons.get(choice, 0) + 1
                    print(f"Added {choice} to your ship!")
                else:
                    character.inventory[choice] = character.inventory.get(choice, 0) + 1
                    print(f"You bought a {choice}!")
            else:
                print("You can't afford this weapon!") 