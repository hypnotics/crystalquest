import random
import pickle
import os
from datetime import datetime
from crystalquest.items import (
    sacred_artifact_abilities, 
    treasure_types, 
    weapons, 
    trade_goods, 
    ship_types
)
from crystalquest.colors import COLORS
from crystalquest.ascii_art import load_ascii_art, display_ascii_art
from crystalquest.ships import Ship, TradeShip
from crystalquest.locations.shipyard import Shipyard
from crystalquest.locations.pub import Pub
from crystalquest.locations.market import Market
from crystalquest.locations.smithy import Smithy
from crystalquest.locations.home import Home
from crystalquest.locations.port import Port
from crystalquest.locations.ruins import Ruins

# Lists for random generation
climates = ["Tropical", "Temperate", "Mediterranean", "Arctic", "Subtropical"]
biotopes = ["Forest", "Mountains", "Rivers", "Lakes", "Grasslands", "Jungle", "Beaches", "Cliffs", "Caves", "Wetlands"]
town_names_prefixes = ["Port", "New", "Old", "East", "West", "North", "South", "Fort", "Bay"]
town_names_suffixes = ["Harbor", "Town", "Village", "Port", "Settlement", "Market", "Haven", "Landing"]
animal_species = ["Fox", "Wolf", "Bear", "Raccoon", "Rabbit", "Deer", "Otter", "Badger", "Squirrel", "Owl", "Cat", "Dog"]
island_prefixes = ["Shadow", "Mystic", "Thunder", "Crystal", "Emerald", "Golden", "Silver"]
island_suffixes = ["Isle", "Island", "Haven", "Bay", "Cove", "Shores", "Point"]
pirate_name_prefixes = ["Captain", "Black", "Red", "Mad", "Cruel", "Salty", "Iron", "Gold", "Silver", "Bloody"]
pirate_name_suffixes = ["Cruelbeard", "Meathook", "Lumpeye", "Sabertooth", "Crookclaw", "Doublefang", "Shadowheart", "Dusthand", "Winterbones", "IceStorm"]

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
        print("\nInventory:")
        if self.inventory:
            for item, amount in self.inventory.items():
                print(f"  {item}: {amount}")
        else:
            print("  Empty")
            
        if self.ship:
            print(f"\nShip: {self.ship.name}")
            print(f"  Crew: {self.ship.current_crew}/{self.ship.crew_capacity}")
            print(f"  Hull: {self.ship.hull_current}/{self.ship.hull_max}")
            if self.ship.weapons:
                print("  Weapons:")
                for weapon, count in self.ship.weapons.items():
                    print(f"    {weapon}: {count}")

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
        
        # Update ruins initialization
        self.has_ruins = random.random() < 0.4  # 40% chance of ruins
        if self.has_ruins:
            self.ruins = Ruins()  # No longer needs type parameter
        
        if not self.is_inhabited:
            self.towns = {}
            self.population = 0
        else:
            self.towns = {}
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
        if self.is_inhabited:
            print("Status: Inhabited")
            print(f"Population: {self.population}")
            print("\nTowns:")
            for town_name in self.towns:
                print(f"- {town_name}")
        else:
            print("Status: Uninhabited")
            if self.has_ruins:
                status = "Unexplored" if not self.ruins.treasure_found else "Explored"
                print(f"Ancient Ruins discovered! ({status})")

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
                    row += " " + COLORS.colorize("@", COLORS.WHITE) + " "
                    continue
                
                # Check for sea monster
                if sea_monster and sea_monster.position == (i, j) and day is not None and day % 3 == 0:
                    row += " " + COLORS.colorize("∞", COLORS.GRAY) + " "
                    continue
                
                # Check for ships
                ship_here = False
                if ships:
                    for ship_pos, ship_type, is_player_ship in ships:
                        if ship_pos == (i, j):
                            if is_player_ship:
                                row += " " + COLORS.colorize("@", COLORS.WHITE) + " "
                            else:
                                row += " " + COLORS.colorize(ship_type[0], COLORS.RED) + " "
                            ship_here = True
                            break
                
                if not ship_here:
                    if self.grid[i][j] is None:
                        row += " " + COLORS.colorize("~", COLORS.BLUE) + " "  # Water
                    else:
                        if self.grid[i][j].is_inhabited:
                            row += " " + COLORS.colorize("I", COLORS.GREEN) + " "  # Inhabited island
                        else:
                            row += " " + COLORS.colorize("o", COLORS.YELLOW) + " "  # Uninhabited island
            print(row)
        
        print("\nLegend:")
        print(COLORS.colorize("@", COLORS.WHITE) + " = You")
        print(COLORS.colorize("I", COLORS.GREEN) + " = Inhabited Island")
        print(COLORS.colorize("o", COLORS.YELLOW) + " = Uninhabited Island")
        print(COLORS.colorize("~", COLORS.BLUE) + " = Water")
        print(COLORS.colorize("S/B/G", COLORS.RED) + " = Sloop/Brigantine/Galleon")
        print(COLORS.colorize("∞", COLORS.GRAY) + " = Sea Monster")

class World:
    def __init__(self, num_islands=5):
        self.map = Map(20)
        self.islands = {}
        
        # Create islands
        for _ in range(num_islands):
            island = Island()
            self.islands[island.name] = island
            island.world = self  # Add reference to world
            
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

        # Calculate max_trade_ships after islands are created
        self.max_trade_ships = len([i for i in self.islands.values() if i.is_inhabited]) * 2  # 2 ships per inhabited island

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
                # Load and display monster art when destroying a ship
                monster_art = load_ascii_art('crystalquest/art/monster.jpeg')
                if monster_art:
                    display_ascii_art(monster_art)
                destroyed.append(ship)
        return destroyed

def main():
    
    # Load and display title art
    title_art = load_ascii_art('crystalquest/art/title.jpeg')
    if title_art:
        display_ascii_art(title_art)
    print("\n")
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
        
        # Check for sea monster collision with current ship
        if ((player.ship and sea_monster.position == player.ship.position) or
            (current_ship and sea_monster.position == current_ship.get_position())):
            print("\nThe sea monster attacks your ship!")
            print(f"{RED}=== GAME OVER ==={RESET}")
            print(f"You survived for {day} days.")
            break
        
        # Check for destroyed ships
        destroyed_ships = sea_monster.check_collisions(trade_ships)
        for ship in destroyed_ships:
            trade_ships.remove(ship)
            if day % 3 == 0:  # Only show message when monster is visible
                print(f"\n{COLORS.colorize('The sea monster has destroyed a ' + ship.type + '!', COLORS.GRAY)}")
        
        # Update trade ships
        for island in world.islands.values():
            if island.is_inhabited:
                for town_name, town in island.towns.items():
                    if 'port' in town.locations:
                        port = town.locations['port']
                        new_ship = port.spawn_trade_ship(day, island, town_name, world)
                        if new_ship:
                            trade_ships.append(new_ship)
                        port.update_trade_ships(trade_ships)
        
        # Move existing trade ships and remove any that are stuck
        active_trade_ships = []
        for ship in trade_ships:
            ship.move()
            if ship.destination or ship.returning_home:
                active_trade_ships.append(ship)
        trade_ships = active_trade_ships
        
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
                day = current_island.ruins.visit(player, day)  # Use return value from visit
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
