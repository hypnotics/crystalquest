import random
import pickle
import os
from datetime import datetime

# Lists for random generation
climates = ["Tropical", "Temperate", "Mediterranean", "Arctic", "Subtropical"]
biotopes = ["Forest", "Mountains", "Rivers", "Lakes", "Grasslands", "Jungle", "Beaches", "Cliffs", "Caves", "Wetlands"]
town_names_prefixes = ["Port", "New", "Old", "East", "West", "North", "South", "Fort", "Bay"]
town_names_suffixes = ["Harbor", "Town", "Village", "Port", "Settlement", "Market", "Haven", "Landing"]
animal_species = ["Fox", "Wolf", "Bear", "Raccoon", "Rabbit", "Deer", "Otter", "Badger", "Squirrel", "Owl", "Cat", "Dog"]
island_prefixes = ["Shadow", "Mystic", "Thunder", "Crystal", "Emerald", "Golden", "Silver"]
island_suffixes = ["Isle", "Island", "Haven", "Bay", "Cove", "Shores", "Point"]
ruin_types = ["Temple", "Fortress", "Palace", "Pyramid", "Monastery", "Amphitheater", "Catacombs", "Lighthouse", "Observatory"]
pirate_name_prefixes = ["Captain", "Black", "Red", "Mad", "Cruel", "Salty", "Iron", "Gold", "Silver", "Bloody"]
pirate_name_suffixes = ["Cruelbeard", "Meathook", "Lumpeye", "Sabertooth", "Crookclaw", "Doublefang", "Shadowheart", "Dusthand", "Winterbones", "IceStorm"]

# Update sacred artifact abilities with specific names
sacred_artifact_abilities = [
    {
        "name": "Warrior's Medallion",
        "description": "An ancient medallion pulsing with martial energy",
        "type": "stat_boost",
        "stat": "Strength",
        "boost": 2
    },
    {
        "name": "Fertile Earth Charm",
        "description": "A mystical charm that resonates with natural energy",
        "type": "farming",
        "growth_reduction": 2
    },
    {
        "name": "Ancient Warrior's Weapon",
        "description": "A perfectly preserved weapon of mysterious origin",
        "type": "weapon",
        "damage": random.randint(3, 7),
        "weapon_type": random.choice(['melee', 'ranged'])
    }
]

treasure_types = [
    {"name": "Golden Idol", "value": 2000},
    {"name": "Ancient Coins", "value": 1500},
    {"name": "Jeweled Crown", "value": 3000},
    {"name": "Sacred Artifact", "value": 2500, "ability": random.choice(sacred_artifact_abilities)},
    {"name": "Royal Scepter", "value": 1800}
]

# Add these color constants at the top of the file
BLUE = '\033[94m'      # Light blue for water
GREEN = '\033[92m'     # Green for inhabited islands
YELLOW = '\033[93m'    # Yellow for uninhabited islands
RED = '\033[91m'       # Red for ships
WHITE = '\033[97m'     # White for player
RESET = '\033[0m'      # Reset color
GRAY = '\033[90m'      # Gray for sea monster

class TradeShip:
    def __init__(self, home_island, world):
        # Ship type
        ship_type = random.choice(['Sloop', 'Brigantine', 'Galleon'])
        ship_stats = {
            'Sloop': {'crew_max': 10, 'speed': 2, 'cargo': 5},
            'Brigantine': {'crew_max': 15, 'speed': 2, 'cargo': 8},
            'Galleon': {'crew_max': 25, 'speed': 1, 'cargo': 12}
        }
        
        self.type = ship_type
        self.crew = random.randint(5, ship_stats[ship_type]['crew_max'])
        self.speed = ship_stats[ship_type]['speed']
        self.cargo_capacity = ship_stats[ship_type]['cargo']
        
        # Location and movement
        self.home_island = home_island
        self.current_position = home_island.coordinates
        self.destination = None
        self.days_at_destination = 0
        self.returning_home = False
        
        # Trade goods
        trade_goods = ['Food', 'Seeds', 'Spices', 'Cloth', 'Rum', 'Wood', 'Iron', 'Gold']
        self.selling = random.choice(trade_goods)
        self.buying = random.choice([g for g in trade_goods if g != self.selling])
        self.sell_price = random.randint(50, 200)
        self.buy_price = random.randint(50, 200)
        
        # Set random destination (not home island)
        available_islands = [island for island in world.islands.values() 
                           if island.is_inhabited and island != home_island]
        if available_islands:
            self.destination = random.choice(available_islands)
        
        self.last_position = self.current_position

    def move(self):
        if not self.destination:
            return
            
        self.last_position = self.current_position  # Store last position before moving
        
        target = (self.home_island.coordinates if self.returning_home 
                 else self.destination.coordinates)
        
        # Calculate direction vector
        dx = target[0] - self.current_position[0]
        dy = target[1] - self.current_position[1]
        distance = (dx**2 + dy**2)**0.5
        
        if distance <= self.speed:
            # Reached destination
            self.current_position = target
            if self.returning_home and target == self.home_island.coordinates:
                # Reset for next journey
                self.returning_home = False
                self.days_at_destination = 0
                self.destination = None
            elif not self.returning_home:
                self.days_at_destination += 1
                if self.days_at_destination >= 3:
                    self.returning_home = True
        else:
            # Move toward destination
            move_x = int(dx / distance * self.speed)
            move_y = int(dy / distance * self.speed)
            self.current_position = (
                self.current_position[0] + move_x,
                self.current_position[1] + move_y
            )

class Ship:
    def __init__(self, name, price, crew_capacity, speed):
        self.name = name
        self.price = price
        self.crew_capacity = crew_capacity
        self.current_crew = 0
        self.speed = speed  # Squares per day
        self.position = None  # Will be set when starting travel
        self.destination = None  # Will be set when starting travel

class Shipyard:
    def __init__(self):
        self.ships = {
            'Sloop': {
                'price': 1000,
                'crew_capacity': 10,
                'speed': 2
            },
            'Brigantine': {
                'price': 2000,
                'crew_capacity': 15,
                'speed': 2
            },
            'Galleon': {
                'price': 3000,
                'crew_capacity': 25,
                'speed': 1
            }
        }

    def visit(self, character):
        print("\n=== Welcome to the Shipyard ===")
        print("Available ships:")
        for ship_name, stats in self.ships.items():
            print(f"{ship_name}: {stats['price']} gold (Crew: {stats['crew_capacity']}, Speed: {stats['speed']} squares/day)")
        
        choice = input("\nWhat would you like to buy? (Enter ship name or 'no'): ").title()
        if choice in self.ships:
            if character.gold >= self.ships[choice]['price']:
                character.gold -= self.ships[choice]['price']
                character.ship = Ship(
                    choice, 
                    self.ships[choice]['price'],
                    self.ships[choice]['crew_capacity'],
                    self.ships[choice]['speed']
                )
                print(f"You bought a {choice}!")
            else:
                print("You can't afford this ship!")

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

class Smithy:
    def __init__(self):
        self.weapons = {
            'Cutlass': {
                'price': 200,
                'damage': 3,
                'type': 'melee'
            },
            'Pistol': {
                'price': 300,
                'damage': 4,
                'type': 'ranged'
            },
            'Musket': {
                'price': 400,
                'damage': 5,
                'type': 'ranged'
            },
            'Boarding Axe': {
                'price': 150,
                'damage': 2,
                'type': 'melee'
            }
        }

    def visit(self, character):
        print("\n=== Welcome to the Smithy ===")
        print("Available weapons:")
        for weapon, stats in self.weapons.items():
            print(f"{weapon}: {stats['price']} gold (Damage: {stats['damage']}, Type: {stats['type']})")

        choice = input("\nWhat would you like to buy? (Enter weapon name or 'no'): ").title()
        if choice in self.weapons:
            if character.gold >= self.weapons[choice]['price']:
                character.gold -= self.weapons[choice]['price']
                character.inventory[choice] = character.inventory.get(choice, 0) + 1
                print(f"You bought a {choice}!")
            else:
                print("You can't afford this weapon!")

class Market:
    def __init__(self):
        self.goods = {
            'Food': 50,
            'Seeds': 30,
            'Spices': 100,
            'Cloth': 80,
            'Rum': 120
        }

    def visit(self, character):
        print("\n=== Welcome to the Market ===")
        print("Available goods:")
        for item, price in self.goods.items():
            print(f"{item}: {price} gold")

        choice = input("\nWhat would you like to buy? (Enter item name or 'no'): ").title()
        if choice in self.goods:
            amount = input("How many would you like to buy? ")
            try:
                amount = int(amount)
                total_cost = amount * self.goods[choice]
                if character.gold >= total_cost:
                    character.gold -= total_cost
                    character.inventory[choice] = character.inventory.get(choice, 0) + amount
                    print(f"You bought {amount} {choice}!")
                else:
                    print("You can't afford that many!")
            except ValueError:
                print("Please enter a valid number!")

class Port:
    def __init__(self):
        self.travel_cost = 200
        self.trade_ships = []  # List of trade ships currently in port
        self.last_spawn = 0  # Days since last trade ship spawn

    def spawn_trade_ship(self, current_day, home_island, world):
        # Count total trade ships in the world
        total_trade_ships = sum(len(port.trade_ships) 
                              for island in world.islands.values() 
                              if island.is_inhabited 
                              for port in [town.locations.get('port') for town in island.towns.values()])
        
        # Only spawn if below max limit and enough time has passed
        if (total_trade_ships < world.max_trade_ships and 
            current_day - self.last_spawn >= random.randint(3, 7)):
            self.trade_ships.append(TradeShip(home_island, world))
            self.last_spawn = current_day

    def handle_trade(self, character, day):
        if not self.trade_ships:
            print("No trade ships currently in port!")
            return None, None, None, day
        # ... rest of handle_trade method ...
        return None, None, None, day

    def handle_deckhand_travel(self, day):
        # Filter out ships with no destination
        available_ships = [ship for ship in self.trade_ships if ship.destination is not None]
        
        if not available_ships:
            print("No ships currently available for travel!")
            return None, None, None, day

        print("\nAvailable ships:")
        for i, ship in enumerate(available_ships, 1):
            dest = "returning home" if ship.returning_home else f"headed to {ship.destination.name}"
            print(f"{i}. {ship.type} ({dest})")
        
        choice = input("\nWhich ship would you like to join? (number or 'cancel'): ")
        if choice.lower() == 'cancel':
            return None, None, None, day
            
        try:
            chosen_ship = available_ships[int(choice) - 1]
            print(f"\nYou've joined the crew of the {chosen_ship.type}!")
            return ((chosen_ship.destination if not chosen_ship.returning_home 
                    else chosen_ship.home_island), None, chosen_ship, day)
        except (ValueError, IndexError):
            print("Invalid choice!")
            return None, None, None, day

    def handle_sailing(self, character, world, current_island, day):
        print("\nUse numpad to navigate:")
        print("7 8 9")
        print("4 5 6")
        print("1 2 3")
        print("(5 to wait, 0 to quit sailing)")
        
        ship_pos = list(current_island.coordinates)
        moves_remaining = character.ship.speed
        
        while True:
            # Display map with current ship position
            world.map.display(tuple(ship_pos))
            
            print(f"\nMoves remaining this day: {moves_remaining}")
            move = input("Enter direction (0-9): ")
            
            # Movement mapping
            moves = {
                '8': (-1, 0),   # North
                '2': (1, 0),    # South
                '6': (0, 1),    # East
                '4': (0, -1),   # West
                '7': (-1, -1),  # Northwest
                '9': (-1, 1),   # Northeast
                '1': (1, -1),   # Southwest
                '3': (1, 1),    # Southeast
                '5': (0, 0),    # Wait
                '0': None       # Quit
            }
            
            if move not in moves:
                print("Invalid direction!")
                continue
                
            if move == '0':
                return current_island, None, None, day
                
            if move == '5':
                print("Waiting...")
                day += 1
                moves_remaining = character.ship.speed
                continue
                
            if moves_remaining <= 0:
                print("No more moves today! Use 5 to wait for next day.")
                continue
                
            dx, dy = moves[move]
            new_x = ship_pos[0] + dx
            new_y = ship_pos[1] + dy
            
            # Check if new position is within bounds
            if 0 <= new_x < world.map.size and 0 <= new_y < world.map.size:
                ship_pos = [new_x, new_y]
                moves_remaining -= 1
                
                # Check if we're on an island
                island_here = world.map.grid[new_x][new_y]
                if island_here:
                    print(f"\nYou've reached {island_here.name}!")
                    disembark = input("Would you like to disembark? (yes/no): ").lower()
                    if disembark == 'yes':
                        return island_here, None, None, day
            else:
                print("You can't sail off the edge of the map!")

        return current_island, None, None, day

    def calculate_distance(self, start, end):
        """Calculate distance between two points using Pythagorean theorem"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        return (dx**2 + dy**2)**0.5

    def calculate_travel_time(self, distance, speed):
        """Calculate travel time based on distance and ship speed"""
        return max(1, int(distance / speed))

    def visit(self, character, world, current_island, day):
        print("\n=== Welcome to the Port ===")
        if character.ship:
            print("1. Set Sail")
            print("2. Trade with Ships")
            print("3. Back")
        else:
            print("1. Travel as Deckhand")
            print("2. Trade with Ships")
            print("3. Back")
        
        choice = input("What would you like to do? ")
        
        if character.ship and choice == "1":
            return self.handle_sailing(character, world, current_island, day)
        elif not character.ship and choice == "1":
            return self.handle_deckhand_travel(day)
        elif choice == "2":
            return self.handle_trade(character, day)
        
        return current_island, None, None, day

class Home:
    def __init__(self):
        self.storage = {}  # For storing items
        self.storage_limit = 10
        self.field = None  # For growing crops
        self.planting_day = None  # To track when something was planted
        
    def visit(self, character, current_day):
        while True:
            print("\n=== Welcome Home ===")
            print("\nStorage:", self.storage)
            print(f"Storage space used: {sum(self.storage.values())}/{self.storage_limit}")
            
            if self.field:
                days_growing = current_day - self.planting_day
                print(f"\nField: {self.field} (Growing for {days_growing} days)")
                if days_growing >= 5:  # Crops take 5 days to grow
                    print("Your crop is ready to harvest!")
            else:
                print("\nField: Empty")
            
            print("\nWhat would you like to do?")
            print("1. Store items")
            print("2. Retrieve items")
            print("3. Plant seeds")
            print("4. Harvest crop")
            print("5. Leave")
            
            choice = input("\nChoice: ")
            
            if choice == "1":
                self._store_items(character)
            elif choice == "2":
                self._retrieve_items(character)
            elif choice == "3":
                self._plant_seeds(character, current_day)
            elif choice == "4":
                self._harvest_crop(character, current_day)
            elif choice == "5":
                break
            else:
                print("Invalid choice!")
    
    def _store_items(self, character):
        print("\nYour inventory:", character.inventory)
        item = input("What would you like to store? (or 'cancel'): ").title()
        
        if item == 'Cancel':
            return
            
        if item in character.inventory:
            amount = int(input(f"How many {item}s would you like to store? "))
            if amount <= 0:
                print("Please enter a positive number!")
                return
                
            if amount > character.inventory[item]:
                print("You don't have that many!")
                return
                
            current_storage = sum(self.storage.values())
            if current_storage + amount > self.storage_limit:
                print("Not enough storage space!")
                return
                
            character.inventory[item] -= amount
            if character.inventory[item] == 0:
                del character.inventory[item]
                
            self.storage[item] = self.storage.get(item, 0) + amount
            print(f"Stored {amount} {item}(s)")
        else:
            print("You don't have that item!")
    
    def _retrieve_items(self, character):
        if not self.storage:
            print("Storage is empty!")
            return
            
        print("\nStored items:", self.storage)
        item = input("What would you like to retrieve? (or 'cancel'): ").title()
        
        if item == 'Cancel':
            return
            
        if item in self.storage:
            amount = int(input(f"How many {item}s would you like to retrieve? "))
            if amount <= 0:
                print("Please enter a positive number!")
                return
                
            if amount > self.storage[item]:
                print("You don't have that many stored!")
                return
                
            character.inventory[item] = character.inventory.get(item, 0) + amount
            self.storage[item] -= amount
            if self.storage[item] == 0:
                del self.storage[item]
            print(f"Retrieved {amount} {item}(s)")
        else:
            print("That item isn't in storage!")
    
    def _plant_seeds(self, character, current_day):
        if self.field:
            print("There's already something growing in your field!")
            return
            
        if "Seeds" not in character.inventory:
            print("You don't have any seeds to plant!")
            return
            
        character.inventory["Seeds"] -= 1
        if character.inventory["Seeds"] == 0:
            del character.inventory["Seeds"]
            
        self.field = "Crops"
        self.planting_day = current_day
        print("You planted some seeds!")
    
    def _harvest_crop(self, character, current_day):
        if not self.field:
            print("There's nothing growing in your field!")
            return
            
        days_growing = current_day - self.planting_day
        if days_growing < 5:
            print(f"The crops aren't ready yet! ({days_growing}/5 days)")
            return
            
        character.inventory["Food"] = character.inventory.get("Food", 0) + 3
        print("You harvested 3 Food from your crops!")
        self.field = None
        self.planting_day = None

class Town:
    def __init__(self, name, is_home_town=False):
        self.name = name
        self.population = random.randint(100, 1000)
        self.locations = {
            'shipyard': Shipyard(),
            'pub': Pub(),
            'smithy': Smithy(),
            'market': Market(),
            'port': Port()
        }
        if is_home_town:
            self.locations['home'] = Home()

class Ruins:
    def __init__(self):
        self.type = random.choice(ruin_types)
        self.explored = False
        
    def explore(self, character):
        if self.explored:
            print("You've already explored these ruins.")
            return
            
        print(f"\nExploring the ancient {self.type}...")
        print("The air is thick with mystery as you venture deeper...")
        
        if random.random() < 0.6:
            self._find_treasure(character)
        else:
            self._encounter_robbers(character)
            
        self.explored = True
    
    def _find_treasure(self, character):
        treasure = random.choice(treasure_types)
        
        # Handle special abilities for Sacred Artifacts
        if treasure['name'] == "Sacred Artifact":
            ability = treasure['ability']
            print(f"\nYou've discovered a {ability['name']}!")
            print(ability['description'])
            print(f"It's worth {treasure['value']} gold!")
            
            if ability['type'] == 'stat_boost':
                character.stats[ability['stat']] += ability['boost']
                print(f"The {ability['name']} increases your {ability['stat']} by {ability['boost']}!")
                
            elif ability['type'] == 'farming':
                character.growth_reduction = ability['growth_reduction']
                print(f"The {ability['name']} will make your crops grow {ability['growth_reduction']} days faster!")
                
            elif ability['type'] == 'weapon':
                weapon_name = f"{ability['name']}"
                character.inventory[weapon_name] = character.inventory.get(weapon_name, 0) + 1
                print(f"The {ability['name']} has {ability['damage']} damage as a {ability['weapon_type']} weapon!")
                if not hasattr(character, 'weapon_stats'):
                    character.weapon_stats = {}
                character.weapon_stats[weapon_name] = {
                    'damage': ability['damage'],
                    'type': ability['weapon_type']
                }
        else:
            print(f"\nYou've discovered a {treasure['name']}!")
            print(f"It's worth {treasure['value']} gold!")
        
        character.gold += treasure['value']
        
    def _encounter_robbers(self, character):
        print("\nYou've encountered a group of robbers!")
        robbers_strength = random.randint(5, 15)
        
        combat_score = (character.stats["Strength"] + 
                       character.stats["Dexterity"] + 
                       character.inventory.get("Cutlass", 0) * 2 +
                       character.inventory.get("Pistol", 0) * 3)
        
        if combat_score > robbers_strength:
            loot = random.randint(100, 500)
            print(f"You've defeated the robbers and found {loot} gold!")
            character.gold += loot
        else:
            loss = min(character.gold, random.randint(50, 200))
            print(f"The robbers overwhelmed you! You lost {loss} gold.")
            character.gold -= loss

class Nemesis:
    def __init__(self):
        self.species = random.choice(animal_species)
        self.name = f"{random.choice(pirate_name_prefixes)} {random.choice(pirate_name_suffixes)}"
        self.ship_type = random.choice(['Sloop', 'Brigantine', 'Galleon'])
        
        # Initialize stats similar to player
        self.stats = {
            "Health": random.randint(7, 12),  # Slightly stronger than player
            "Intelligence": random.randint(5, 10),
            "Charisma": random.randint(5, 10),
            "Strength": random.randint(5, 10),
            "Dexterity": random.randint(5, 10),
            "Psyche": random.randint(5, 10)
        }

class Character:
    def __init__(self):
        self.species = random.choice(animal_species)
        self.name = input("Enter your character's name: ")
        self.island = None
        self.gold = 1000
        self.ship = None
        self.crew = []
        self.inventory = {}
        self.weapon_stats = {}
        
        self.stats = {
            "Health": random.randint(5, 10),
            "Intelligence": random.randint(1, 10),
            "Charisma": random.randint(1, 10),
            "Strength": random.randint(1, 10),
            "Dexterity": random.randint(1, 10),
            "Psyche": random.randint(1, 10)
        }
        
        # Create nemesis
        self.nemesis = Nemesis()
        
        print(f"\nYour father has disappeared with his ship in the last storm.") 
        print(f"\nHe's left you with a family artifact, a spyglass, a map of the silent seas, and a thousand commonwealth goldcoins.") 

        # Add starting items to inventory
        self.inventory["Spyglass"] = 1
        self.inventory["Silent Seas Map"] = 1

        print(f"\nHis nemesis, the feared {self.nemesis.species} pirate {self.nemesis.name}, has sworn to seek and destroy your family. He's looking for you. Be Prepared!")
        print(f"Last seen commanding a {self.nemesis.ship_type}.")

        # Give player a random sacred artifact at start
        starting_artifact = random.choice(sacred_artifact_abilities)
        print(f"\nYour family artifact is a {starting_artifact['name']}!")
        print(starting_artifact['description'])
        
        # Add artifact to inventory regardless of type
        self.inventory[starting_artifact['name']] = 1
        
        if starting_artifact['type'] == 'stat_boost':
            self.stats[starting_artifact['stat']] += starting_artifact['boost']
            print(f"The {starting_artifact['name']} increases your {starting_artifact['stat']} by {starting_artifact['boost']}!")
            
        elif starting_artifact['type'] == 'farming':
            self.growth_reduction = starting_artifact['growth_reduction']
            print(f"The {starting_artifact['name']} will make your crops grow {starting_artifact['growth_reduction']} days faster!")
            
        elif starting_artifact['type'] == 'weapon':
            # Weapon stats are already added to inventory above
            self.weapon_stats[starting_artifact['name']] = {
                'damage': starting_artifact['damage'],
                'type': starting_artifact['weapon_type']
            }
            print(f"The {starting_artifact['name']} has {starting_artifact['damage']} damage as a {starting_artifact['weapon_type']} weapon!")

    def display_info(self):
        print("\n=== Character Information ===")
        print(f"Name: {self.name}")
        print(f"Species: {self.species}")
        print(f"Home Island: {self.island}")
        print("\n=== Stats ===")
        for stat, value in self.stats.items():
            print(f"{stat}: {value}")
        print("\n=== Nemesis Information ===")
        print(f"Name: {self.nemesis.name} the {self.nemesis.species}")
        print(f"Ship: {self.nemesis.ship_type}")

class Island:
    def __init__(self, name=None):
        if name is None:
            self.name = f"{random.choice(island_prefixes)} {random.choice(island_suffixes)}"
        else:
            self.name = name
            
        self.size = random.choice(["Small", "Medium", "Large"])
        self.climate = random.choice(climates)
        self.coordinates = None  # Initialize coordinates attribute
        
        num_biotopes = {
            "Small": random.randint(2, 3),
            "Medium": random.randint(3, 5),
            "Large": random.randint(5, 7)
        }[self.size]
        self.biotopes = random.sample(biotopes, num_biotopes)
        
        self.is_inhabited = random.random() > 0.3
        
        if not self.is_inhabited:
            self.has_ruins = True # random.random() < 0.4
            self.ruins = Ruins() if self.has_ruins else None
            self.towns = {}
            self.population = 0
        else:
            self.has_ruins = False
            self.ruins = None
            num_towns = {
                "Small": 1,
                "Medium": 2,
                "Large": 3
            }[self.size]
            
            self.towns = {}
            for _ in range(num_towns):
                town_name = f"{random.choice(town_names_prefixes)} {random.choice(town_names_suffixes)}"
                self.towns[town_name] = Town(town_name)
            
            self.population = sum(town.population for town in self.towns.values())

    def display_info(self):
        print(f"\n=== {self.name} ===")
        print(f"Size: {self.size}")
        print(f"Climate: {self.climate}")
        if self.coordinates:
            # Convert grid coordinates to lat/long format
            lat = f"{'N' if self.coordinates[0] < 10 else 'S'} {abs(self.coordinates[0] - 10):02.1f}°"
            long = f"{'W' if self.coordinates[1] < 10 else 'E'} {abs(self.coordinates[1] - 10):02.1f}°"
            print(f"Location: {lat}, {long}")
            print(f"Grid Position: ({self.coordinates[0]}, {self.coordinates[1]})")
        print(f"Biotopes: {', '.join(self.biotopes)}")
        if self.is_inhabited:
            print(f"Total Population: {self.population}")
            print("\nTowns:")
            for town_name, town in self.towns.items():
                print(f"- {town_name} (Population: {town.population})")
        else:
            print("Status: Uninhabited")
            if self.has_ruins:
                status = "Unexplored" if not self.ruins.explored else "Explored"
                print(f"Ancient {self.ruins.type} discovered! ({status})")

class Map:
    def __init__(self, size=20):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        
    def place_island(self, island, x, y):
        # Get island size in grid squares
        sizes = {
            "Small": [(0,0)],  # 1 square
            "Medium": [(0,0), (0,1), (1,0), (1,1)],  # 4 squares
            "Large": [(i,j) for i in range(3) for j in range(3)]  # 9 squares
        }
        
        island_squares = sizes[island.size]
        
        # Calculate the buffer zone (including island size and 2-square water gap)
        buffer = {
            "Small": [(i,j) for i in range(-2,2) for j in range(-2,2)],
            "Medium": [(i,j) for i in range(-2,4) for j in range(-2,4)],
            "Large": [(i,j) for i in range(-2,5) for j in range(-2,5)]
        }
        
        # Check if we can place the island here (including buffer zone)
        # First check the buffer zone for other islands
        for dx, dy in buffer[island.size]:
            check_x, check_y = x + dx, y + dy
            if 0 <= check_x < self.size and 0 <= check_y < self.size:
                if self.grid[check_x][check_y] is not None:
                    return False
        
        # Then check if the island itself fits on the map
        for dx, dy in island_squares:
            new_x, new_y = x + dx, y + dy
            if not (0 <= new_x < self.size and 0 <= new_y < self.size):
                return False
        
        # Place the island and store its coordinates
        island.coordinates = (x, y)  # Set the island's coordinates
        for dx, dy in island_squares:
            self.grid[x + dx][y + dy] = island
        return True
    
    def display(self, player_pos=None, ships=None, sea_monster=None, day=None):
        print("\n=== World Map ===")
        print("   " + " ".join(f"{i:2}" for i in range(self.size)))
        for i in range(self.size):
            row = f"{i:2} "
            for j in range(self.size):
                # Check player position first
                if player_pos and (i, j) == player_pos:
                    row += f" {WHITE}@{RESET} "
                    continue
                
                # Check for sea monster (only show every third day)
                if sea_monster and sea_monster.position == (i, j) and day is not None and day % 3 == 0:
                    row += f" {GRAY}{sea_monster.symbol}{RESET} "
                    continue
                
                # Check for ships
                ship_here = False
                if ships:
                    for ship_pos, ship_type, is_player_ship in ships:
                        if ship_pos == (i, j):
                            if is_player_ship:
                                row += f" {WHITE}@{RESET} "
                            else:
                                row += f" {RED}{ship_type[0]}{RESET} "
                            ship_here = True
                            break
                
                if not ship_here:
                    if self.grid[i][j] is None:
                        row += f" {BLUE}~{RESET} "  # Water
                    else:
                        if self.grid[i][j].is_inhabited:
                            row += f" {GREEN}I{RESET} "  # Inhabited island
                        else:
                            row += f" {YELLOW}o{RESET} "  # Uninhabited island
            print(row)
        
        print("\nLegend:")
        print(f"{WHITE}@{RESET} = You")
        print(f"{GREEN}I{RESET} = Inhabited Island")
        print(f"{YELLOW}o{RESET} = Uninhabited Island")
        print(f"{BLUE}~{RESET} = Water")
        print(f"{RED}S/B/G{RESET} = Sloop/Brigantine/Galleon")
        print(f"{GRAY}∞{RESET} = Sea Monster")

class World:
    def __init__(self, num_islands=5):
        self.map = Map(20)
        self.islands = {}
        self.max_trade_ships = len([i for i in self.islands.values() if i.is_inhabited]) * 4
        
        # Create islands
        for _ in range(num_islands):
            island = Island()
            self.islands[island.name] = island
            
            # Try to place the island on the map
            placed = False
            max_attempts = 100
            attempts = 0
            
            while not placed and attempts < max_attempts:
                x = random.randint(0, self.map.size - 1)
                y = random.randint(0, self.map.size - 1)
                placed = self.map.place_island(island, x, y)
                attempts += 1
            
            if not attempts < max_attempts:
                print(f"Warning: Could not place {island.name} on the map")
        
        # Ensure at least two inhabited islands
        inhabited_count = sum(1 for island in self.islands.values() if island.is_inhabited)
        if inhabited_count < 2:
            # Get list of uninhabited islands
            uninhabited = [name for name, island in self.islands.items() 
                         if not island.is_inhabited]
            
            # Calculate how many more inhabited islands we need
            needed = 2 - inhabited_count
            
            # Convert that many uninhabited islands to inhabited
            for island_name in random.sample(uninhabited, needed):
                self.islands[island_name] = Island(island_name)  # Create new inhabited island
                self.islands[island_name].is_inhabited = True
                self.islands[island_name].towns = {}
                num_towns = {
                    "Small": 1,
                    "Medium": 2,
                    "Large": 3
                }[self.islands[island_name].size]
                
                for _ in range(num_towns):
                    town_name = f"{random.choice(town_names_prefixes)} {random.choice(town_names_suffixes)}"
                    self.islands[island_name].towns[town_name] = Town(town_name)
                
                self.islands[island_name].population = sum(
                    town.population for town in self.islands[island_name].towns.values()
                )

    def get_inhabited_islands(self):
        return {name: island for name, island in self.islands.items() if island.is_inhabited}

    def display_islands(self, current_coordinates=None):
        self.map.display(current_coordinates)
        print("\n=== Island Details ===")
        for island in self.islands.values():
            island.display_info()
            print()

def save_game(player, world, current_island, current_town, day):
    """Save the current game state to a file"""
    save_data = {
        'player': player,
        'world': world,
        'current_island': current_island,
        'current_town': current_town,
        'day': day
    }
    
    # Create saves directory if it doesn't exist
    if not os.path.exists('saves'):
        os.makedirs('saves')
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"saves/save_{timestamp}.dat"
    
    try:
        with open(filename, 'wb') as f:
            pickle.dump(save_data, f)
        print(f"\nGame saved successfully as {filename}")
    except Exception as e:
        print(f"\nError saving game: {e}")

def load_game():
    """Load a saved game state from a file"""
    # Check if saves directory exists
    if not os.path.exists('saves'):
        print("\nNo saved games found!")
        return None
    
    # Get list of save files
    save_files = sorted([f for f in os.listdir('saves') if f.endswith('.dat')], reverse=True)
    
    if not save_files:
        print("\nNo saved games found!")
        return None
    
    print("\nAvailable saved games:")
    for i, save_file in enumerate(save_files, 1):
        # Convert filename timestamp to readable date
        timestamp = save_file[5:-4]  # Remove 'save_' and '.dat'
        date = datetime.strptime(timestamp, '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i}. {date}")
    
    choice = input("\nWhich save would you like to load? (number or 'cancel'): ")
    if choice.lower() == 'cancel':
        return None
    
    try:
        save_file = save_files[int(choice) - 1]
        with open(f"saves/{save_file}", 'rb') as f:
            save_data = pickle.load(f)
        print("\nGame loaded successfully!")
        return save_data
    except Exception as e:
        print(f"\nError loading game: {e}")
        return None

class SeaMonster:
    def __init__(self, world):
        self.speed = 1
        self.symbol = '∞'
        # Find a valid starting position (water only)
        while True:
            self.position = (random.randint(0, world.map.size-1), 
                           random.randint(0, world.map.size-1))
            if not self._is_island(self.position, world):
                break
    
    def move(self, world):
        # Try to move in a random direction
        for _ in range(4):  # Try up to 4 times to find a valid move
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            new_pos = (self.position[0] + dx * self.speed, 
                      self.position[1] + dy * self.speed)
            
            # Check if new position is valid (within bounds and not on island)
            if (0 <= new_pos[0] < world.map.size and 
                0 <= new_pos[1] < world.map.size and 
                not self._is_island(new_pos, world)):
                self.position = new_pos
                break
    
    def _is_island(self, position, world):
        return world.map.grid[position[0]][position[1]] is not None
    
    def check_collisions(self, trade_ships):
        # Return list of ships that collided with monster
        destroyed = []
        for ship in trade_ships:
            if ship.current_position == self.position:
                destroyed.append(ship)
        return destroyed

def main():
    print("Welcome to Crystal Quest! Adventure awaits!")
    print("1. New Game")
    print("2. Load Game")
    choice = input("\nWhat would you like to do? ")
    
    if choice == "2":
        save_data = load_game()
        if save_data:
            player = save_data['player']
            world = save_data['world']
            current_island = save_data['current_island']
            current_town = save_data['current_town']
            day = save_data['day']
        else:
            print("\nStarting new game...")
            world = World(num_islands=5)
            world.display_islands()
            player = Character()
            inhabited_islands = world.get_inhabited_islands()
            player.island = random.choice(list(inhabited_islands.keys()))
            current_island = world.islands[player.island]
            current_town = random.choice(list(current_island.towns.keys()))
            current_island.towns[current_town] = Town(current_town, is_home_town=True)
            day = 1
    else:
        # New game initialization
        print("Generating world...")
        world = World(num_islands=5)
        player = Character()
        inhabited_islands = world.get_inhabited_islands()
        player.island = random.choice(list(inhabited_islands.keys()))
        current_island = world.islands[player.island]
        current_town = random.choice(list(current_island.towns.keys()))
        current_island.towns[current_town] = Town(current_town, is_home_town=True)
        day = 1
    
    trade_ships = []
    sea_monster = SeaMonster(world)
    
    current_ship = None  # Add this variable to track if player is on a ship
    
    while True:
        print(f"\n=== Day {day} ===")
        
        # Move sea monster
        sea_monster.move(world)
        
        # Check if sea monster caught the player
        if ((not current_ship and sea_monster.position == current_island.coordinates) or
            (current_ship and sea_monster.position == tuple(ship_pos))):
            print(f"\n{GRAY}The sea monster has found you!{RESET}")
            print(f"{RED}=== GAME OVER ==={RESET}")
            print(f"You survived for {day} days.")
            break
        
        # Check for destroyed ships
        destroyed_ships = sea_monster.check_collisions(trade_ships)
        for ship in destroyed_ships:
            trade_ships.remove(ship)
            if day % 3 == 0:  # Only show message when monster is visible
                print(f"\n{GRAY}The sea monster has destroyed a {ship.type}!{RESET}")
        
        # Update trade ships
        for island in world.islands.values():
            if island.is_inhabited:
                for town_name, town in island.towns.items():
                    if 'port' in town.locations:
                        port = town.locations['port']
                        port.spawn_trade_ship(day, island, world)
                        trade_ships.extend([ship for ship in port.trade_ships if ship not in trade_ships])
        
        # Move existing trade ships
        for ship in trade_ships:
            ship.move()
        
        # Create ship display info list with player ship information
        ship_display_info = [(ship.current_position, ship.type, ship == current_ship) 
                            for ship in trade_ships]
        
        # Display map with trade ships and sea monster
        world.map.display(
            None if current_ship else current_island.coordinates, 
            ship_display_info,
            sea_monster,
            day
        )
        
        # Check for ships arriving at player's location
        if current_island and not current_ship:  # Only check if player is on an island
            for ship in trade_ships:
                # Check if ship just arrived at player's location
                if (ship.current_position == current_island.coordinates and 
                    ship.last_position != current_island.coordinates):
                    dest_type = "home port" if ship.returning_home else "destination"
                    print(f"\nA {ship.type} has arrived at its {dest_type}!")
        
        # Different menu options when at sea
        if current_ship:
            print(f"\n=== Aboard {current_ship.type} ===")
            print("1. View Character Info")
            print("2. View Ship Info")
            print("3. Wait")
            print("4. Save Game")
            print("5. Quit")
            
            choice = input("\nWhat would you like to do? ")
            
            if choice == "1":
                player.display_info()
            elif choice == "2":
                print(f"\n=== Ship Information ===")
                print(f"Type: {current_ship.type}")
                print(f"Crew: {current_ship.crew}")
                print(f"Speed: {current_ship.speed} squares/day")
                if current_ship.returning_home:
                    print(f"Destination: {current_ship.home_island.name} (Home Port)")
                else:
                    print(f"Destination: {current_ship.destination.name}")
            elif choice == "3":
                print("You wait for a day...")
                day += 1
                
                # Move sea monster and update ships
                sea_monster.move(world)
                for ship in trade_ships:
                    ship.move()
                
                # Check if ship has reached destination
                if (current_ship.current_position == 
                    (current_ship.destination.coordinates if not current_ship.returning_home 
                     else current_ship.home_island.coordinates)):
                    print("\nThe ship has reached its destination!")
                    embark = input("Would you like to disembark? (yes/no): ")
                    if embark.lower() == 'yes':
                        current_island = (current_ship.destination if not current_ship.returning_home 
                                        else current_ship.home_island)
                        if current_island.is_inhabited:
                            current_town = random.choice(list(current_island.towns.keys()))
                            print(f"\nYou disembark and step onto the docks of {current_island.name}!")
                            print(f"You find yourself in the town of {current_town}.")
                            # Display town menu immediately
                            print(f"\n=== {current_town}, {current_island.name} ===")
                            print("1. Shipyard")
                            print("2. Pub")
                            print("3. Smithy")
                            print("4. Market")
                            print("5. Port")
                            print("6. View Character Info")
                            print("7. View Island Info")
                            print("8. Wait")
                            print("9. Save Game")
                            if 'home' in current_island.towns[current_town].locations:
                                print("10. Home")
                                print("11. Quit")
                            else:
                                print("10. Quit")
                        else:
                            print("The island appears to be uninhabited.")
                        current_ship = None
            elif choice == "4":
                save_game(player, world, current_island, current_town, day)
            elif choice == "5":
                print("Thanks for playing!")
                break
            else:
                print("Invalid choice!")
                
            continue  # Skip the rest of the loop when on a ship

        # Town menu options only shown when not on a ship
        elif current_island.is_inhabited and current_town is not None:
            print(f"\n=== {current_town}, {current_island.name} ===")
            print("1. Shipyard")
            print("2. Pub")
            print("3. Smithy")
            print("4. Market")
            print("5. Port")
            print("6. View Character Info")
            print("7. View Island Info")
            print("8. Wait")
            print("9. Save Game")
            if 'home' in current_island.towns[current_town].locations:
                print("10. Home")
                print("11. Quit")
            else:
                print("10. Quit")
        else:  # Either uninhabited island or no current town
            print(f"\n=== {current_island.name} ===")
            if not current_island.is_inhabited:
                print("1. View Island Info")
                print("2. Explore Ruins") if current_island.has_ruins else None
                print("3. Return to Port")
                print("4. Wait")
                print("5. Quit")
            else:
                # For inhabited islands where we haven't selected a town yet
                while True:  # Keep asking until valid selection
                    print("Available towns:")
                    for i, town_name in enumerate(current_island.towns.keys(), 1):
                        print(f"{i}. {town_name}")
                    choice = input("\nWhich town would you like to enter? ")
                    try:
                        town_name = list(current_island.towns.keys())[int(choice) - 1]
                        current_town = town_name
                        break  # Exit loop on valid selection
                    except (ValueError, IndexError):
                        print("Invalid choice! Please select a valid town number.")
                continue  # Restart main loop with selected town
        
        choice = input("\nWhat would you like to do? ")
        
        if current_island.is_inhabited:
            if choice == "1":
                current_island.towns[current_town].locations['shipyard'].visit(player)
            elif choice == "2":
                current_island.towns[current_town].locations['pub'].visit(player)
            elif choice == "3":
                current_island.towns[current_town].locations['smithy'].visit(player)
            elif choice == "4":
                current_island.towns[current_town].locations['market'].visit(player)
            elif choice == "5":
                new_island, new_town, new_ship, day = current_island.towns[current_town].locations['port'].visit(
                    player, world, current_island, day)
                if new_ship is not None:
                    current_ship = new_ship
                elif new_island is not None:
                    current_island = new_island
                    current_town = new_town
            elif choice == "6":
                player.display_info()
                print(f"\nGold: {player.gold}")
                print("Inventory:", player.inventory)
                if player.ship:
                    print(f"Ship: {player.ship.name} (Crew: {player.ship.current_crew}/{player.ship.crew_capacity})")
            elif choice == "7":
                current_island.display_info()
            elif choice == "8":
                print("You wait for a day...")
                day += 1
            elif choice == "9":
                save_game(player, world, current_island, current_town, day)
            elif choice == "10" and 'home' in current_island.towns[current_town].locations:
                current_island.towns[current_town].locations['home'].visit(player, day)
            elif (choice == "11" and 'home' in current_island.towns[current_town].locations) or \
                 (choice == "10" and 'home' not in current_island.towns[current_town].locations):
                print("Thanks for playing!")
                break
            else:
                print("Invalid choice!")
        else:
            if choice == "1":
                current_island.display_info()
            elif choice == "2" and current_island.has_ruins:
                current_island.ruins.explore(player)
                day += 1  # Exploring ruins takes a day
            elif choice == "3":
                # Return to nearest inhabited island
                inhabited_islands = world.get_inhabited_islands()
                if inhabited_islands:
                    current_island = list(inhabited_islands.values())[0]
                    current_town = random.choice(list(current_island.towns.keys()))
                    print(f"\nReturned to {current_island.name}!")
                day += 1  # Travel takes a day
            elif choice == "4":
                print("You wait for a day...")
                day += 1
            elif choice == "5":
                print("Thanks for playing!")
                break
            else:
                print("Invalid choice!")

if __name__ == "__main__":
    main()
