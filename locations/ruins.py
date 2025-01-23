import random
from crystalquest.items import treasure_types

class Ruins:
    def __init__(self):
        self.treasure_found = False
        self.treasure_types = treasure_types

    def visit(self, character, day):
        print("\n=== Ancient Ruins ===")
        
        if self.treasure_found:
            print("You've already explored these ruins.")
            return day
            
        print("You explore the ancient ruins...")
        
        # 30% chance to find treasure
        if random.random() < 0.3:
            treasure = random.choice(self.treasure_types)
            print(f"\nYou found a {treasure['name']}!")
            
            if 'ability' in treasure:
                print(f"It's a {treasure['ability']['name']}!")
                print(f"{treasure['ability']['description']}")
                
                if treasure['ability']['type'] == 'stat_boost':
                    print(f"Your {treasure['ability']['stat']} increased by {treasure['ability']['boost']}!")
                    # Apply stat boost here
                elif treasure['ability']['type'] == 'farming':
                    print("This will help crops grow faster!")
                elif treasure['ability']['type'] == 'weapon':
                    print(f"You got a weapon that does {treasure['ability']['damage']} damage!")
                    
            character.gold += treasure['value']
            print(f"You gained {treasure['value']} gold!")
            self.treasure_found = True
            
        else:
            print("You found nothing of value.")
            
        return day + 1 