import random
from crystalquest.prompts import ask

class Home:
    def __init__(self):
        self.rest_heal = 10
        self.crops = []  # {"ready": day, "crop": name}

    def _pending(self):
        """Older saves stored crops as a dict keyed by the day they ripen."""
        if isinstance(self.crops, dict):
            self.crops = [{"ready": ready, "crop": crop} for ready, crop in self.crops.items()]
        if not isinstance(self.crops, list):
            self.crops = []
        return self.crops

    def _harvest(self, character, day):
        pending = self._pending()
        remaining = []
        for plot in pending:
            ready = plot.get("ready", day + 1)
            if ready <= day:
                crop = plot.get("crop", "Food")
                character.inventory[crop] = character.inventory.get(crop, 0) + 1
                print(f"Your {crop} has grown and is ready to harvest!")
            else:
                remaining.append(plot)
        self.crops = remaining

    def visit(self, character, day):
        print("\n=== Welcome Home ===")
        character.ensure_vitals()
        self._harvest(character, day)
        print("1. Rest and heal")
        print("2. Grow crops")
        print("3. Leave")

        choice = ask("\nWhat would you like to do? ")
        if choice == "1":
            gained = character.heal(self.rest_heal)
            if gained <= 0:
                print(f"You are already fully rested ({character.stats['Health']}/{character.max_health}).")
                return day
            print(f"You rest for the day and recover {gained} health "
                  f"({character.stats['Health']}/{character.max_health}).")
            return day + 1
        elif choice == "2":
            seeds = character.inventory.get("Seeds", 0)
            if not isinstance(seeds, int) or seeds <= 0:
                print("You don't have any seeds to plant!")
                return day

            if len(self._pending()) >= 3:
                print("Your garden is full! Wait for some crops to grow.")
                return day

            character.inventory["Seeds"] = seeds - 1
            if character.inventory["Seeds"] <= 0:
                del character.inventory["Seeds"]

            growth_time = random.randint(3, 7)
            growth_time = max(1, growth_time - getattr(character, 'growth_reduction', 0))
            self._pending().append({"ready": day + growth_time, "crop": "Food"})
            print(f"You planted some seeds! They will grow in {growth_time} days.")
            return day + 1

        return day
