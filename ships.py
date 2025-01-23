import random
from crystalquest.items import ship_types, trade_goods

class Ship:
    def __init__(self, name, price, crew_capacity, speed):
        self.name = name
        self.price = price
        self.crew_capacity = crew_capacity
        self.current_crew = 0
        self.speed = speed
        self.weapons = {}
        self.position = None
        self.destination = None
        # Add hull attributes
        self.hull_max = ship_types[name]['hull_max']
        self.hull_current = self.hull_max

    def is_mobile(self):
        return self.hull_current >= 10

    def repair_at_sea(self, character):
        """Repair ship using wood from cargo"""
        if self.hull_current >= self.hull_max:
            print("Ship is already at full health!")
            return False
        
        if 'Wood' not in character.inventory:
            print("You need wood to repair the ship!")
            return False

        character.inventory['Wood'] -= 1
        if character.inventory['Wood'] == 0:
            del character.inventory['Wood']
            
        self.hull_current = min(self.hull_current + 15, self.hull_max)
        print(f"Repaired ship hull to {self.hull_current}/{self.hull_max}")
        return True

class TradeShip:
    def __init__(self, home_island, world):
        # Ship type
        ship_type = random.choice(list(ship_types.keys()))
        stats = ship_types[ship_type]
        
        self.type = ship_type
        self.crew = random.randint(5, stats['crew_max'])
        self.speed = stats['speed']
        self.cargo_capacity = stats['cargo']
        
        # Location and movement
        self.home_island = home_island
        self.current_position = home_island.coordinates
        self.destination = None
        self.days_at_destination = 0
        self.returning_home = False
        
        # Trade goods
        self.selling = random.choice(list(trade_goods.keys()))
        self.buying = random.choice([g for g in trade_goods.keys() if g != self.selling])
        self.sell_price = random.randint(50, 200)
        self.buy_price = random.randint(50, 200)
        
        # Set random destination (not home island)
        self.set_new_destination(world)
        
        self.last_position = self.current_position

    def set_new_destination(self, world):
        """Set a new random destination for the trade ship"""
        available_islands = [island for island in world.islands.values() 
                           if island.is_inhabited and island != self.home_island]
        if available_islands:
            self.destination = random.choice(available_islands)
            self.returning_home = False
            self.days_at_destination = 0

    def get_position(self):
        """Return current position as tuple for map display"""
        return tuple(self.current_position)

    def move(self):
        if not self.destination and not self.returning_home:
            self.set_new_destination(self.home_island.world)  # Need to pass world reference
            return
            
        self.last_position = self.current_position
        
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
                self.set_new_destination(self.home_island.world)
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