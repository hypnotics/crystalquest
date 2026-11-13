import random
import pickle
import os
from datetime import datetime
from crystalquest.items import (
    weapons,
    ship_types,
    make_artifact,
)
from crystalquest.colors import COLORS, RED, RESET
from crystalquest.prompts import ask
from crystalquest.ascii_art import load_ascii_art, display_ascii_art
from crystalquest.locations.shipyard import Shipyard
from crystalquest.locations.pub import Pub
from crystalquest.locations.market import Market
from crystalquest.locations.smithy import Smithy
from crystalquest.locations.home import Home
from crystalquest.locations.port import Port
from crystalquest.locations.ruins import Ruins
from crystalquest.monsters import SeaMonster

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

def _as_pos(pos):
    """Return a map coordinate as a pair of ints, or None."""
    if pos is None:
        return None
    try:
        return (int(pos[0]), int(pos[1]))
    except (TypeError, ValueError, IndexError):
        return None

def _chebyshev(a, b):
    if a is None or b is None:
        return None
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

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
        self.speed = ship_types[self.ship_type]['speed']

        # Initialize stats similar to player
        self.stats = {
            "Health": random.randint(8, 12),  # Slightly stronger than player
            "Intelligence": random.randint(5, 10),
            "Charisma": random.randint(5, 10),
            "Strength": random.randint(6, 10),
            "Dexterity": random.randint(5, 10),
            "Psyche": random.randint(5, 10)
        }
        self.max_health = self.stats["Health"]
        self.position = None
        self.absent_until = 0
        self.hunting = True

    def ensure_state(self):
        """Fill in fields missing from a save made before the hunt existed."""
        if not hasattr(self, 'position'):
            self.position = None
        if not hasattr(self, 'absent_until'):
            self.absent_until = 0
        if not hasattr(self, 'hunting'):
            self.hunting = True
        if not hasattr(self, 'speed'):
            stats = ship_types.get(getattr(self, 'ship_type', 'Sloop'), ship_types['Sloop'])
            self.speed = stats['speed']
        if not hasattr(self, 'max_health'):
            self.max_health = max(1, self.stats.get("Health", 1))
        if self.stats.get("Health", 1) < 1:
            self.stats["Health"] = self.max_health

    def place(self, world, avoid=None, min_distance=8):
        self.ensure_state()
        size = world.map.size
        avoid_pos = _as_pos(avoid)
        for _ in range(300):
            pos = (random.randint(0, size - 1), random.randint(0, size - 1))
            if world.map.grid[pos[0]][pos[1]] is not None:
                continue
            if avoid_pos is not None and _chebyshev(pos, avoid_pos) < min_distance:
                continue
            self.position = pos
            self.hunting = True
            return
        self.position = next(
            ((x, y) for x in range(size) for y in range(size) if world.map.grid[x][y] is None),
            (0, 0)
        )
        self.hunting = True

    def _island_at(self, world, pos):
        pos = _as_pos(pos)
        if pos is None:
            return None
        if not (0 <= pos[0] < world.map.size and 0 <= pos[1] < world.map.size):
            return None
        return world.map.grid[pos[0]][pos[1]]

    def _caught(self, world, target_pos):
        target = _as_pos(target_pos)
        if self.position is None or target is None:
            return False
        if tuple(self.position) == target:
            return True
        here = self._island_at(world, self.position)
        there = self._island_at(world, target)
        return here is not None and here is there

    def step_toward(self, world, target):
        target = _as_pos(target)
        if self.position is None or target is None:
            return
        x, y = self.position
        dx = 0 if x == target[0] else (1 if target[0] > x else -1)
        dy = 0 if y == target[1] else (1 if target[1] > y else -1)
        nx, ny = x + dx, y + dy
        if 0 <= nx < world.map.size and 0 <= ny < world.map.size:
            self.position = (nx, ny)

    def pursue(self, world, target_pos, day, player, steps=None):
        """Sail toward the player and fight on contact. At most one fight a day."""
        self.ensure_state()
        if day < self.absent_until:
            return
        if self.position is None:
            self.place(world, avoid=target_pos)
            self.hunting = True
            print(f"\nWord arrives that {self.name} is back on the water.")
            return
        if _as_pos(target_pos) is None:
            return

        if steps is None:
            steps = max(1, self.speed)
        for _ in range(max(0, steps)):
            if self._caught(world, target_pos):
                break
            self.step_toward(world, target_pos)

        if self._caught(world, target_pos) and getattr(self, '_fought_day', None) != day:
            self.fight(player, world, day)
            return

        distance = None if self.position is None else _chebyshev(self.position, _as_pos(target_pos))
        if distance is not None and distance <= 4 and getattr(self, '_warned_day', None) != day:
            self._warned_day = day
            print(f"\nLookouts spot {self.name}'s {self.ship_type} on the horizon!")

    def fight(self, player, world, day):
        self.ensure_state()
        self._fought_day = day
        player.ensure_vitals()
        print(f"\n{self.name} the {self.species} catches you!")
        print(f"The {self.ship_type} draws alongside and {self.name} boards!")

        weapon = player.weapon_damage()
        player_roll = (player.stats.get("Strength", 1) + player.stats.get("Dexterity", 1) // 2
                       + weapon + random.randint(1, 6))
        enemy_roll = (self.stats.get("Strength", 1) + self.stats.get("Dexterity", 1) // 2
                      + random.randint(1, 8))

        if player_roll >= enemy_roll:
            dealt = max(1, player_roll - enemy_roll)
            self.stats["Health"] -= dealt
            print(f"You strike {self.name} for {dealt} damage!")
            if self.stats["Health"] <= 0:
                bounty = random.randint(150, 400)
                player.gold += bounty
                print(f"{self.name} is defeated and drops {bounty} gold.")
                print("A pirate like that will not stay gone forever.")
                self.stats["Health"] = self.max_health
                self.absent_until = day + random.randint(5, 8)
                self.position = None
                self.hunting = False
                return
            print(f"{self.name} still has {self.stats['Health']} health and breaks off.")
        else:
            dealt = max(1, enemy_roll - player_roll)
            before = player.stats["Health"]
            player.stats["Health"] = max(1, before - dealt)
            taken = before - player.stats["Health"]
            if taken:
                print(f"You take {taken} damage! (Health: {player.stats['Health']}/{player.max_health})")
            else:
                print(f"You stay on your feet. (Health: {player.stats['Health']}/{player.max_health})")
            ship = getattr(player, 'ship', None)
            if ship is not None and getattr(ship, 'hull_current', 0) > 10:
                hull_hit = min(dealt, ship.hull_current - 10)
                ship.hull_current -= hull_hit
                if hull_hit:
                    print(f"Your hull is scarred ({ship.hull_current}/{ship.hull_max}).")
            stolen = min(getattr(player, 'gold', 0), random.randint(20, 80))
            if stolen:
                player.gold -= stolen
                print(f"{self.name} snatches {stolen} gold and falls back.")
            else:
                print(f"{self.name} finds no coin and falls back.")

        self.hunting = True
        self.place(world, avoid=self.position, min_distance=8)

class Character:
    def __init__(self):
        self.species = random.choice(animal_species)
        self.name = ask("Enter your character's name: ").strip() or "Sailor"
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
        self.max_health = self.stats["Health"]

        # Create nemesis
        self.nemesis = Nemesis()

        print(f"\nYour father has disappeared with his ship in the last storm.")
        print(f"\nHe's left you with a family artifact, a spyglass, a map of the silent seas, and a thousand commonwealth goldcoins.")

        # Add starting items to inventory
        self.inventory["Spyglass"] = 1
        self.inventory["Silent Seas Map"] = 1

        print(f"\nHis nemesis, the feared {self.nemesis.species} pirate {self.nemesis.name}, has sworn to seek and destroy your family. He's looking for you. Be Prepared!")
        print(f"Last seen commanding a {self.nemesis.ship_type}.")

        starting_artifact = make_artifact()
        self.apply_artifact(
            starting_artifact,
            lead=f"\nYour family artifact is a {starting_artifact['name']}!"
        )

    def ensure_vitals(self):
        if not hasattr(self, 'weapon_stats') or self.weapon_stats is None:
            self.weapon_stats = {}
        if not hasattr(self, 'inventory') or self.inventory is None:
            self.inventory = {}
        if not hasattr(self, 'stats') or not self.stats:
            self.stats = {"Health": 1}
        health = self.stats.get("Health", 1)
        if not isinstance(health, int) or health < 1:
            health = 1
        self.stats["Health"] = health
        if not getattr(self, 'max_health', None):
            self.max_health = health
        if not hasattr(self, 'gold') or self.gold is None:
            self.gold = 0

    def heal(self, amount):
        self.ensure_vitals()
        before = self.stats["Health"]
        self.stats["Health"] = min(self.max_health, before + max(0, amount))
        return self.stats["Health"] - before

    def weapon_damage(self):
        self.ensure_vitals()
        best = 0
        for name, stats in self.weapon_stats.items():
            if self.inventory.get(name, 0) > 0 and isinstance(stats, dict):
                best = max(best, stats.get('damage', 0))
        for name, count in self.inventory.items():
            stats = weapons.get(name)
            if not count or not isinstance(stats, dict) or stats.get('type') == 'ship':
                continue
            best = max(best, stats.get('damage', 0))
        return best

    def apply_artifact(self, artifact, lead=None):
        """Add an artifact and apply its stat, farming, or weapon effect."""
        if not isinstance(artifact, dict):
            return
        self.ensure_vitals()
        name = artifact.get('name', 'Artifact')
        self.inventory[name] = self.inventory.get(name, 0) + 1
        if lead:
            print(lead)
        else:
            print(f"\nYou receive a {name}!")
        if artifact.get('description'):
            print(artifact['description'])

        kind = artifact.get('type')
        if kind == 'stat_boost':
            stat = artifact.get('stat', 'Strength')
            boost = artifact.get('boost', 0)
            self.stats[stat] = self.stats.get(stat, 0) + boost
            if stat == 'Health':
                self.max_health += boost
            print(f"The {name} increases your {stat} by {boost}!")
        elif kind == 'farming':
            reduction = artifact.get('growth_reduction', 1)
            self.growth_reduction = getattr(self, 'growth_reduction', 0) + reduction
            print(f"The {name} will make your crops grow {reduction} days faster!")
        elif kind == 'weapon':
            damage = artifact.get('damage', 1)
            weapon_type = artifact.get('weapon_type', 'melee')
            self.weapon_stats[name] = {'damage': damage, 'type': weapon_type}
            print(f"The {name} has {damage} damage as a {weapon_type} weapon!")

    def display_info(self):
        self.ensure_vitals()
        print("\n=== Character Information ===")
        print(f"Name: {self.name}")
        print(f"Species: {self.species}")
        print(f"Home Island: {self.island}")
        print("\n=== Stats ===")
        for stat, value in self.stats.items():
            if stat == "Health":
                print(f"Health: {value}/{self.max_health}")
            else:
                print(f"{stat}: {value}")
        print(f"Gold: {self.gold}")
        print("\n=== Nemesis Information ===")
        nemesis = self.nemesis
        nemesis.ensure_state()
        print(f"Name: {nemesis.name} the {nemesis.species}")
        print(f"Ship: {nemesis.ship_type}")
        if nemesis.hunting and nemesis.position is not None:
            print(f"Status: hunting you ({nemesis.stats.get('Health', '?')} health)")
        elif not nemesis.hunting:
            print(f"Status: recovering until day {nemesis.absent_until}")
        else:
            print("Status: hunting you")
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
        
        # Check if we can place the island
        if self.can_place_island(island, x, y):
            # Place the island in all its squares
            for dx, dy in island_squares:
                self.grid[x + dx][y + dy] = island
            
            # Set the island's coordinates to its top-left corner
            island.coordinates = (x, y)
            return True
            
        return False

    def can_place_island(self, island, x, y):
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
        
        return True
    
    def display(self, player_pos=None, ships=None, sea_monster=None, day=None, nemesis=None):
        player_pos = _as_pos(player_pos)
        nemesis_pos = _as_pos(getattr(nemesis, 'position', None)) if nemesis is not None else None
        monster_pos = _as_pos(getattr(sea_monster, 'position', None)) if sea_monster is not None else None
        print("\n=== World Map ===")
        print("   " + " ".join(f"{i:2}" for i in range(self.size)))
        for i in range(self.size):
            row = f"{i:2} "
            for j in range(self.size):
                # Check player position first
                if player_pos and (i, j) == player_pos:
                    row += " " + COLORS.colorize("@", COLORS.WHITE) + " "
                    continue

                if nemesis_pos and (i, j) == nemesis_pos:
                    row += " " + COLORS.colorize("N", COLORS.RED) + " "
                    continue

                # Check for sea monster
                if monster_pos and (i, j) == monster_pos:
                    row += " " + COLORS.colorize("∞", COLORS.GRAY) + " "
                    continue
                
                # Check for ships
                ship_here = False
                if ships:
                    for ship_pos, ship_type, is_player_ship in ships:
                        if _as_pos(ship_pos) == (i, j):
                            if is_player_ship:
                                row += " " + COLORS.colorize("@", COLORS.WHITE) + " "
                            else:
                                marker = (ship_type or "S")[0]
                                row += " " + COLORS.colorize(marker, COLORS.RED) + " "
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
        print(COLORS.colorize("N", COLORS.RED) + " = Nemesis")
        print(COLORS.colorize("∞", COLORS.GRAY) + " = Sea Monster")

class World:
    def __init__(self, num_islands=5):
        self.map = Map(20)
        self.islands = {}
        self.sea_monster = SeaMonster(self)

        attempts = 0
        while len(self.islands) < num_islands and attempts < num_islands * 30:
            attempts += 1
            island = Island()
            island.world = self
            renamed = 0
            while island.name in self.islands and renamed < 20:
                island.name = f"{random.choice(island_prefixes)} {random.choice(island_suffixes)}"
                renamed += 1
            if island.name in self.islands:
                continue

            placed = False
            for _ in range(100):
                x = random.randint(0, self.map.size - 1)
                y = random.randint(0, self.map.size - 1)
                if self.map.place_island(island, x, y):
                    placed = True
                    break
            if placed:
                self.islands[island.name] = island

        if not any(island.coordinates for island in self.islands.values()):
            self._place_fallback_island()

        # Keep the island object already on the map. Replacing it used to
        # leave the new harbor with no coordinates, which crashed sailing.
        self._ensure_two_harbors()
        harbors = len([i for i in self.islands.values() if i.is_inhabited])
        self.max_trade_ships = max(2, harbors * 2)

    def _fresh_town_name(self, island):
        for _ in range(30):
            name = f"{random.choice(town_names_prefixes)} {random.choice(town_names_suffixes)}"
            if name not in island.towns:
                return name
        return f"Camp {len(island.towns) + 1}"

    def _add_towns(self, island):
        if island.towns:
            island.population = sum(town.population for town in island.towns.values())
            return
        num_towns = {"Small": 1, "Medium": 2, "Large": 3}.get(island.size, 1)
        for _ in range(num_towns):
            town_name = self._fresh_town_name(island)
            island.towns[town_name] = Town(town_name)
        island.population = sum(town.population for town in island.towns.values())

    def _ensure_two_harbors(self):
        def ready(island):
            return island.is_inhabited and island.coordinates and island.towns

        if sum(1 for island in self.islands.values() if ready(island)) >= 2:
            return
        for island in list(self.islands.values()):
            if not island.coordinates:
                continue
            if not ready(island):
                island.is_inhabited = True
                self._add_towns(island)
            if sum(1 for candidate in self.islands.values() if ready(candidate)) >= 2:
                return

    def _place_fallback_island(self):
        island = Island("Safe Haven")
        island.world = self
        island.size = "Small"
        island.is_inhabited = True
        self._add_towns(island)
        placed = False
        for x in range(self.map.size - 1):
            for y in range(self.map.size - 1):
                if self.map.place_island(island, x, y):
                    placed = True
                    break
            if placed:
                break
        if placed:
            self.islands[island.name] = island

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
    
    choice = ask("\nWhich save would you like to load? (number or 'cancel'): ")
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

def collect_trade_ships(world):
    ships = []
    for island in world.islands.values():
        if not getattr(island, 'is_inhabited', False):
            continue
        for town in island.towns.values():
            port = town.locations.get('port') if getattr(town, 'locations', None) else None
            if not port:
                continue
            for ship in getattr(port, 'trade_ships', []):
                if ship not in ships:
                    ships.append(ship)
    return ships

def ship_markers(trade_ships):
    markers = []
    for ship in trade_ships:
        pos = _as_pos(getattr(ship, 'current_position', None))
        if pos is None:
            continue
        markers.append((pos, getattr(ship, 'type', 'Ship') or 'Ship', False))
    return markers

def player_world_position(current_island, current_ship):
    if current_ship is not None:
        pos = _as_pos(getattr(current_ship, 'current_position', None))
        if pos is not None:
            return pos
    if current_island is not None:
        return _as_pos(getattr(current_island, 'coordinates', None))
    return None

def ship_destination_coords(ship):
    if getattr(ship, 'returning_home', False) and getattr(ship, 'home_island', None) is not None:
        return _as_pos(getattr(ship.home_island, 'coordinates', None))
    dest = getattr(ship, 'destination', None)
    if dest is None:
        return None
    return _as_pos(getattr(dest, 'coordinates', None))

def describe_voyage(current_ship):
    print("\n=== Ship Information ===")
    print(f"Type: {getattr(current_ship, 'type', getattr(current_ship, 'name', 'Ship'))}")
    crew = getattr(current_ship, 'crew', None)
    if crew is None and hasattr(current_ship, 'current_crew'):
        crew = f"{current_ship.current_crew}/{getattr(current_ship, 'crew_capacity', '?')}"
    print(f"Crew: {crew}")
    print(f"Speed: {getattr(current_ship, 'speed', '?')} squares/day")
    if getattr(current_ship, 'returning_home', False) and getattr(current_ship, 'home_island', None) is not None:
        print(f"Destination: {current_ship.home_island.name} (Home Port)")
    elif getattr(current_ship, 'destination', None) is not None:
        print(f"Destination: {current_ship.destination.name}")
    else:
        print("Destination: unknown waters")

def offer_disembark(current_ship, current_island, current_town, day):
    """Ask once per day when a hired ship is sitting at its destination."""
    target = ship_destination_coords(current_ship)
    position = _as_pos(getattr(current_ship, 'current_position', None))
    if target is None or position is None or position != target:
        return current_ship, current_island, current_town
    if getattr(current_ship, '_declined_landing', None) == (target, day):
        return current_ship, current_island, current_town

    print("\nThe ship has reached its destination!")
    if ask("Would you like to disembark? (yes/no): ").strip().lower() != 'yes':
        current_ship._declined_landing = (target, day)
        return current_ship, current_island, current_town

    if getattr(current_ship, 'returning_home', False) and getattr(current_ship, 'home_island', None) is not None:
        island = current_ship.home_island
    else:
        island = getattr(current_ship, 'destination', None) or current_island
    town = current_town
    if island is not None and island.is_inhabited and island.towns:
        town = random.choice(list(island.towns.keys()))
        print(f"\nYou disembark and step onto the docks of {island.name}!")
        print(f"You find yourself in the town of {town}.")
    elif island is not None:
        town = None
        print(f"\nYou step onto {island.name}. The island appears to be uninhabited.")
    return None, island, town

def harbors(world):
    return [island for island in world.islands.values()
            if island.is_inhabited and island.coordinates and island.towns]

def begin_new_game():
    print("Generating world...")
    world = World(num_islands=5)
    player = Character()
    choices = harbors(world)
    if not choices:
        print("The chart shows no harbors. The voyage cannot begin.")
        raise SystemExit(1)
    current_island = random.choice(choices)
    player.island = current_island.name
    current_town = random.choice(list(current_island.towns.keys()))
    current_island.towns[current_town] = Town(current_town, is_home_town=True)
    day = 1
    trade_ships = []
    port = current_island.towns[current_town].locations['port']
    ship = port.spawn_trade_ship(day, current_island, current_town, world, force=True)
    if ship:
        trade_ships.append(ship)
    player.nemesis.place(world, avoid=current_island.coordinates)
    return player, world, current_island, current_town, day, trade_ships

def restore_loaded_game(save_data):
    player = save_data['player']
    world = save_data['world']
    current_island = save_data.get('current_island')
    current_town = save_data.get('current_town')
    day = save_data.get('day', 1) or 1
    player.ensure_vitals()
    if getattr(player, 'nemesis', None) is not None:
        player.nemesis.ensure_state()
        if player.nemesis.position is None and day >= player.nemesis.absent_until:
            avoid = getattr(current_island, 'coordinates', None) if current_island else None
            player.nemesis.place(world, avoid=avoid)
    if current_island is None or not getattr(current_island, 'coordinates', None):
        choices = harbors(world)
        if not choices:
            print("This save has no land left to stand on.")
            raise SystemExit(1)
        current_island = choices[0]
        current_town = next(iter(current_island.towns))
    return player, world, current_island, current_town, day, collect_trade_ships(world)

def morning_update(world, trade_ships, day, player, current_island, current_ship):
    """Spawn, move, and hunt once for this day."""
    for island in list(world.islands.values()):
        if not getattr(island, 'is_inhabited', False):
            continue
        for town_name, town in island.towns.items():
            port = town.locations.get('port') if getattr(town, 'locations', None) else None
            if not port:
                continue
            new_ship = port.spawn_trade_ship(day, island, town_name, world)
            if new_ship and new_ship not in trade_ships:
                trade_ships.append(new_ship)
            port.update_trade_ships(trade_ships)

    still_sailing = []
    for ship in trade_ships:
        ship.move()
        if getattr(ship, 'destination', None) or getattr(ship, 'returning_home', False):
            still_sailing.append(ship)
    trade_ships[:] = still_sailing

    monster = getattr(world, 'sea_monster', None)
    if monster is not None:
        monster.move(world)
        destroyed = monster.check_collisions(trade_ships)
        if destroyed:
            print(f"\n{RED}The sea monster has destroyed {len(destroyed)} ships!{RESET}")
            trade_ships[:] = [ship for ship in trade_ships if ship not in destroyed]

    nemesis = getattr(player, 'nemesis', None)
    if nemesis is not None and hasattr(nemesis, 'pursue'):
        nemesis.pursue(world, player_world_position(current_island, current_ship), day, player)

def show_world(world, trade_ships, day, player, current_island, current_ship):
    nemesis = getattr(player, 'nemesis', None)
    monster = getattr(world, 'sea_monster', None)
    world.map.display(
        player_world_position(current_island, current_ship),
        ship_markers(trade_ships),
        monster,
        day,
        nemesis
    )
    if current_island and not current_ship:
        here = _as_pos(current_island.coordinates)
        for ship in trade_ships:
            pos = _as_pos(getattr(ship, 'current_position', None))
            last = _as_pos(getattr(ship, 'last_position', None))
            if pos is not None and pos == here and last != here:
                dest_type = "home port" if getattr(ship, 'returning_home', False) else "destination"
                print(f"\nA {ship.type} has arrived at its {dest_type}!")

def main():
    title_art = load_ascii_art('crystalquest/art/title.jpeg')
    if title_art:
        display_ascii_art(title_art)
    print("\n")
    print("Welcome to Crystal Quest! Adventure awaits!")
    print("1. New Game")
    print("2. Load Game")
    choice = ask("\nWhat would you like to do? ").strip()

    if choice == "2":
        save_data = load_game()
        if save_data:
            player, world, current_island, current_town, day, trade_ships = restore_loaded_game(save_data)
        else:
            print("\nStarting new game...")
            player, world, current_island, current_town, day, trade_ships = begin_new_game()
    else:
        player, world, current_island, current_town, day, trade_ships = begin_new_game()

    current_ship = None
    resolved_day = None

    while True:
        print(f"\n=== Day {day} ===")

        if resolved_day != day:
            morning_update(world, trade_ships, day, player, current_island, current_ship)
            resolved_day = day

        show_world(world, trade_ships, day, player, current_island, current_ship)

        if current_ship:
            current_ship, current_island, current_town = offer_disembark(
                current_ship, current_island, current_town, day)
        if current_ship:
            print(f"\n=== Aboard {getattr(current_ship, 'type', 'ship')} ===")
            print("1. View Character Info")
            print("2. View Ship Info")
            print("3. Wait")
            print("4. Save Game")
            print("5. Quit")
            try:
                choice = ask("\nWhat would you like to do? ").strip()
                if choice == "1":
                    player.display_info()
                elif choice == "2":
                    describe_voyage(current_ship)
                elif choice == "3":
                    print("You wait for a day...")
                    day += 1
                elif choice == "4":
                    save_game(player, world, current_island, current_town, day)
                elif choice == "5":
                    print("Thanks for playing!")
                    break
                else:
                    print("Invalid choice!")
            except Exception as exc:
                print(f"\nThat action failed ({exc}). You remain aboard.")
            continue

        if current_island is None:
            print("You are lost at sea.")
            break

        try:
            if current_island.is_inhabited and (current_town not in current_island.towns):
                current_town = None

            if current_island.is_inhabited and current_town is not None:
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
            elif not current_island.is_inhabited:
                print(f"\n=== {current_island.name} ===")
                print("1. View Island Info")
                if current_island.has_ruins:
                    print("2. Explore Ruins")
                print("3. Return to Port")
                print("4. Wait")
                print("5. Quit")
            else:
                if not current_island.towns:
                    print(f"{current_island.name} has no town left standing.")
                    current_island.is_inhabited = False
                    continue
                while True:
                    print("Available towns:")
                    town_names = list(current_island.towns.keys())
                    for i, town_name in enumerate(town_names, 1):
                        print(f"{i}. {town_name}")
                    choice = ask("\nWhich town would you like to enter? ").strip()
                    try:
                        current_town = town_names[int(choice) - 1]
                        break
                    except (ValueError, IndexError):
                        print("Invalid choice! Please select a valid town number.")
                continue

            choice = ask("\nWhat would you like to do? ").strip()

            if current_island.is_inhabited:
                town = current_island.towns[current_town]
                if choice == "1":
                    town.locations['shipyard'].visit(player)
                elif choice == "2":
                    town.locations['pub'].visit(player)
                elif choice == "3":
                    town.locations['smithy'].visit(player)
                elif choice == "4":
                    town.locations['market'].visit(player)
                elif choice == "5":
                    result = town.locations['port'].visit(
                        player, world, current_island, day, trade_ships)
                    if not result or len(result) != 4:
                        print("The port master has nothing for you.")
                    else:
                        new_island, new_town, new_ship, day = result
                        # Days spent sailing already moved the world.
                        resolved_day = day
                        if new_ship is not None:
                            current_ship = new_ship
                        elif new_island is not None and new_island is not current_island:
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
                elif choice == "10" and 'home' in town.locations:
                    day = town.locations['home'].visit(player, day)
                elif (choice == "11" and 'home' in town.locations) or \
                     (choice == "10" and 'home' not in town.locations):
                    print("Thanks for playing!")
                    break
                else:
                    print("Invalid choice!")
            else:
                if choice == "1":
                    current_island.display_info()
                elif choice == "2" and current_island.has_ruins:
                    day = current_island.ruins.visit(player, day)
                elif choice == "3":
                    destinations = harbors(world)
                    if destinations:
                        current_island = destinations[0]
                        current_town = random.choice(list(current_island.towns.keys()))
                        print(f"\nReturned to {current_island.name}!")
                    else:
                        print("There is no harbor to return to.")
                    day += 1
                elif choice == "4":
                    print("You wait for a day...")
                    day += 1
                elif choice == "5":
                    print("Thanks for playing!")
                    break
                else:
                    print("Invalid choice!")
        except Exception as exc:
            print(f"\nThat action failed ({exc}). You remain where you are.")

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        print(f"\nSomething went wrong and the voyage cannot continue ({exc}).")
        raise SystemExit(1)
