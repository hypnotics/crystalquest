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
                'speed': 3  # Fast but small
            },
            'Brigantine': {
                'price': 2000,
                'crew_capacity': 15,
                'speed': 2  # Medium speed and size
            },
            'Galleon': {
                'price': 3000,
                'crew_capacity': 25,
                'speed': 1  # Slow but large
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
        # Spawn new trade ship every 3-7 days
        if current_day - self.last_spawn >= random.randint(3, 7):
            self.trade_ships.append(TradeShip(home_island, world))
            self.last_spawn = current_day

    def handle_trade(self, character):
        if not self.trade_ships:
            print("No trade ships currently in port!")
            return
            
        print("\n=== Trading Ships in Port ===")
        for i, ship in enumerate(self.trade_ships, 1):
            print(f"\nShip {i} ({ship.type}):")
            print(f"Selling: {ship.selling} for {ship.sell_price} gold")
            print(f"Buying: {ship.buying} for {ship.buy_price} gold")
        
        choice = input("\nWhich ship would you like to trade with? (number or 'cancel'): ")
        if choice.lower() == 'cancel':
            return
            
        try:
            ship = self.trade_ships[int(choice) - 1]
            print("\n1. Buy goods")
            print("2. Sell goods")
            trade_choice = input("What would you like to do? ")
            
            if trade_choice == "1":
                if character.gold >= ship.sell_price:
                    character.gold -= ship.sell_price
                    character.inventory[ship.selling] = (
                        character.inventory.get(ship.selling, 0) + 1
                    )
                    print(f"Bought 1 {ship.selling} for {ship.sell_price} gold")
                else:
                    print("Not enough gold!")
                    
            elif trade_choice == "2":
                if ship.buying in character.inventory and character.inventory[ship.buying] > 0:
                    character.inventory[ship.buying] -= 1
                    if character.inventory[ship.buying] == 0:
                        del character.inventory[ship.buying]
                    character.gold += ship.buy_price
                    print(f"Sold 1 {ship.buying} for {ship.buy_price} gold")
                else:
                    print(f"You don't have any {ship.buying}!")
                    
        except (ValueError, IndexError):
            print("Invalid choice!")

    def visit(self, character, world, current_island):
        print("\n=== Welcome to the Port ===")
        print("1. Travel")
        print("2. Trade with Ships")
        choice = input("What would you like to do? ")
        
        if choice == "2":
            self.handle_trade(character)
            return current_island, None
        elif choice == "1":
            if character.ship is None:
                print("You need a ship before you can travel!")
                return current_island, None

            print("\nAvailable destinations:")
            available_islands = [name for name in world.islands.keys() if name != current_island.name]
            
            for i, island_name in enumerate(available_islands, 1):
                island = world.islands[island_name]
                status = "Inhabited" if island.is_inhabited else "Uninhabited"
                if island.coordinates and current_island.coordinates:
                    distance = self.calculate_distance(current_island.coordinates, island.coordinates)
                    travel_time = self.calculate_travel_time(distance, character.ship.speed)
                    print(f"{i}. {island_name} ({status}) - {distance:.1f} squares away, {travel_time} days to travel")
                else:
                    print(f"{i}. {island_name} ({status})")
            
            print(f"\nTravel cost: {self.travel_cost} gold")
            choice = input("\nWhere would you like to sail? (Enter number or 'no'): ")
            
            try:
                if choice.lower() == 'no':
                    return current_island, None
                    
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(available_islands):
                    if character.gold >= self.travel_cost:
                        character.gold -= self.travel_cost
                        destination_island = world.islands[available_islands[choice_idx]]
                        
                        # Calculate travel time
                        distance = self.calculate_distance(current_island.coordinates, destination_island.coordinates)
                        travel_time = self.calculate_travel_time(distance, character.ship.speed)
                        
                        print(f"\nThe journey will take {travel_time} days.")
                        return destination_island, None
                    else:
                        print("You can't afford to travel!")
                else:
                    print("Invalid destination!")
            except ValueError:
                print("Please enter a valid number!")
            
            return current_island, None

    def calculate_distance(self, start, end):
        """Calculate distance between two points using Pythagorean theorem"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        return (dx**2 + dy**2)**0.5

    def calculate_travel_time(self, distance, speed):
        """Calculate travel time based on distance and ship speed"""
        return max(1, int(distance / speed))

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
                       len(character.inventory.get("Cutlass", [])) * 2 +
                       len(character.inventory.get("Pistol", [])) * 3)
        
        if combat_score > robbers_strength:
            loot = random.randint(100, 500)
            print(f"You've defeated the robbers and found {loot} gold!")
            character.gold += loot
        else:
            loss = min(character.gold, random.randint(50, 200))
            print(f"The robbers overwhelmed you! You lost {loss} gold.")
            character.gold -= loss

class Character:
    def __init__(self):
        self.species = random.choice(animal_species)
        self.name = input("Enter your character's name: ")
        self.island = None  # We'll set this in main() instead
        self.gold = 1000
        self.ship = None
        self.crew = []
        self.inventory = {}
        self.weapon_stats = {}  # Initialize weapon_stats
        
        self.stats = {
            "Health": random.randint(5, 10),
            "Intelligence": random.randint(1, 10),
            "Charisma": random.randint(1, 10),
            "Strength": random.randint(1, 10),
            "Dexterity": random.randint(1, 10),
            "Psyche": random.randint(1, 10)
        }
        
        # Give player a random sacred artifact at start
        starting_artifact = random.choice(sacred_artifact_abilities)
        print(f"\nYou begin your journey with a {starting_artifact['name']}!")
        print(starting_artifact['description'])
        
        if starting_artifact['type'] == 'stat_boost':
            self.stats[starting_artifact['stat']] += starting_artifact['boost']
            print(f"The {starting_artifact['name']} increases your {starting_artifact['stat']} by {starting_artifact['boost']}!")
            
        elif starting_artifact['type'] == 'farming':
            self.growth_reduction = starting_artifact['growth_reduction']
            print(f"The {starting_artifact['name']} will make your crops grow {starting_artifact['growth_reduction']} days faster!")
            
        elif starting_artifact['type'] == 'weapon':
            weapon_name = f"{starting_artifact['name']}"
            self.inventory[weapon_name] = 1
            self.weapon_stats[weapon_name] = {
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
            self.has_ruins = random.random() < 0.4
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
    
    def display(self, current_coordinates=None, trade_ships=None, sea_monster=None, day=None):
        print("\n=== World Map ===")
        print("   " + " ".join(f"{i:2}" for i in range(self.size)))
        for i in range(self.size):
            row = f"{i:2} "
            for j in range(self.size):
                # Always check player position first
                if current_coordinates and (i, j) == current_coordinates:
                    row += f" {WHITE}@{RESET} "  # Player's current location
                    continue
                
                # Check for sea monster (only show every third day)
                monster_here = False
                if (sea_monster and sea_monster.position == (i, j) and 
                    day is not None and day % 3 == 0):
                    row += f" {GRAY}{sea_monster.symbol}{RESET} "
                    monster_here = True
                    continue
                
                # Check for trade ships
                ship_here = False
                if trade_ships and not monster_here:
                    for ship_pos, ship_type in trade_ships:
                        if ship_pos == (i, j):
                            row += f" {RED}{ship_type[0]}{RESET} "
                            ship_here = True
                            break
                
                if not (monster_here or ship_here):
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
        self.map = Map(20)  # Changed to 20x20 grid
        self.islands = {}
        
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
        
        # Ensure at least one inhabited island
        if not any(island.is_inhabited for island in self.islands.values()):
            random_island_name = random.choice(list(self.islands.keys()))
            self.islands[random_island_name] = Island()
            self.islands[random_island_name].is_inhabited = True

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

class TradeShip:
    def __init__(self, home_island, world):
        # Ship type
        ship_type = random.choice(['Sloop', 'Brigantine', 'Galleon'])
        ship_stats = {
            'Sloop': {'crew_max': 10, 'speed': 3, 'cargo': 5},
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
    
    def move(self):
        if not self.destination:
            return
            
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
    print("Welcome to the Island Adventure!")
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
    
    while True:
        print(f"\n=== Day {day} ===")
        
        # Move sea monster
        sea_monster.move(world)
        
        # Check if sea monster caught the player
        if sea_monster.position == current_island.coordinates:
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
        
        # Display map with trade ships and sea monster
        world.map.display(current_island.coordinates, 
                         [(ship.current_position, ship.type) for ship in trade_ships],
                         sea_monster,
                         day)
        
        if current_island.is_inhabited:
            print(f"\n=== {current_town}, {current_island.name} ===")
            print("1. Shipyard")
            print("2. Pub")
            print("3. Smithy")
            print("4. Market")
            print("5. Port")
            print("6. View Character Info")
            print("7. View Island Info")
            print("8. Wait")
            print("9. Save Game")  # New option
            if 'home' in current_island.towns[current_town].locations:
                print("10. Home")
                print("11. Quit")
            else:
                print("10. Quit")
        else:
            print(f"\n=== Uninhabited {current_island.name} ===")
            print("1. View Island Info")
            print("2. Explore Ruins") if current_island.has_ruins else None
            print("3. Return to Port")
            print("4. Wait")  # New option
            print("5. Quit")
        
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
                new_island, new_town = current_island.towns[current_town].locations['port'].visit(player, world, current_island)
                if new_island is not None:
                    current_island = new_island
                    if current_island.is_inhabited:
                        current_town = random.choice(list(current_island.towns.keys()))
                    print(f"\nWelcome to {current_island.name}!")
                day += 1  # Travel takes a day
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
