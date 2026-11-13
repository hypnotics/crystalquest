from crystalquest.items import weapons, ship_types
from crystalquest.prompts import ask

class Smithy:
    def __init__(self):
        self.weapons = weapons

    def _cargo_used(self, character):
        ship = character.ship
        if ship is None:
            return 0
        if not hasattr(ship, 'cargo_capacity'):
            stats = ship_types.get(getattr(ship, 'name', ''), {})
            ship.cargo_capacity = stats.get('cargo', 10)
        used = 0
        for name, count in getattr(ship, 'weapons', {}).items():
            space = self.weapons.get(name, {}).get('cargo_space', 1)
            try:
                used += space * int(count)
            except (TypeError, ValueError):
                continue
        return used

    def visit(self, character):
        print("\n=== Welcome to the Smithy ===")
        print("Available weapons:")

        available_weapons = {}
        for name, stats in self.weapons.items():
            if stats.get('type') == 'ship':
                if character.ship:
                    available_weapons[name] = stats
            else:
                available_weapons[name] = stats

        if not available_weapons:
            print("The smith has nothing for sale.")
            return

        for weapon, stats in available_weapons.items():
            if stats['type'] == 'ship':
                print(f"{weapon}: {stats['price']} gold (Damage: {stats['damage']}, "
                      f"Cargo Space: {stats['cargo_space']}, {stats['description']})")
            else:
                print(f"{weapon}: {stats['price']} gold (Damage: {stats['damage']}, "
                      f"Type: {stats['type']})")

        raw = ask("\nWhat would you like to buy? (Enter weapon name or 'no'): ").strip()
        if raw.lower() in ('no', 'cancel', ''):
            return
        choice = raw.title()
        if choice not in available_weapons:
            print("No weapon by that name.")
            return

        weapon_stats = available_weapons[choice]
        if weapon_stats['type'] == 'ship':
            if character.ship is None:
                print("You need a ship to mount that.")
                return
            used = self._cargo_used(character)
            if used + weapon_stats['cargo_space'] > character.ship.cargo_capacity:
                print("Not enough cargo space on your ship!")
                return

        price = weapon_stats.get('price', 0)
        if character.gold < price:
            print("You can't afford this weapon!")
            return

        character.gold -= price
        if getattr(character, 'weapon_stats', None) is None:
            character.weapon_stats = {}
        if weapon_stats['type'] == 'ship':
            if not hasattr(character.ship, 'weapons') or character.ship.weapons is None:
                character.ship.weapons = {}
            character.ship.weapons[choice] = character.ship.weapons.get(choice, 0) + 1
            print(f"Added {choice} to your ship!")
        else:
            character.inventory[choice] = character.inventory.get(choice, 0) + 1
            character.weapon_stats[choice] = {
                'damage': weapon_stats.get('damage', 1),
                'type': weapon_stats.get('type', 'melee')
            }
            print(f"You bought a {choice}!")
