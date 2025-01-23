class Home:
    def __init__(self):
        self.rest_heal = 10

    def visit(self, character, day):
        print("\n=== Welcome Home ===")
        print("1. Rest and heal")
        print("2. Leave")
        
        choice = input("\nWhat would you like to do? ")
        if choice == "1":
            print(f"You rest for the day and heal {self.rest_heal} health")
            character.health = min(character.health + self.rest_heal, character.max_health)
            return day + 1
        return day 