import random
from crystalquest.items import make_treasure

class Ruins:
    def __init__(self):
        self.treasure_found = False

    def visit(self, character, day):
        print("\n=== Ancient Ruins ===")

        if self.treasure_found:
            print("You've already explored these ruins.")
            return day

        print("You explore the ancient ruins...")

        # 30% chance to find treasure
        if random.random() < 0.3:
            treasure = make_treasure()
            name = treasure.get("name", "Relic")
            print(f"\nYou found a {name}!")

            ability = treasure.get("ability")
            if isinstance(ability, dict):
                character.apply_artifact(ability)
            else:
                character.inventory[name] = character.inventory.get(name, 0) + 1

            value = treasure.get("value", 0)
            if isinstance(value, int) and value > 0:
                character.gold += value
                print(f"You gained {value} gold!")
            self.treasure_found = True
        else:
            print("You found nothing of value.")

        return day + 1
