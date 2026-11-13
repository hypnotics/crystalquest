import random
from crystalquest.items import ship_types, trade_goods

class Ship:
    def __init__(self, name, price, crew_capacity, speed):
        self.name = name
        self.price = price
        self.crew_capacity = crew_capacity
        self.current_crew = 0
        self.speed = speed or 1
        self.weapons = {}
        self.position = None
        self.destination = None
        stats = ship_types.get(name, {})
        self.hull_max = stats.get('hull_max', 30)
        self.hull_current = self.hull_max
        self.cargo_capacity = stats.get('cargo', 10)

    def is_mobile(self):
        return self.hull_current >= 10

    def repair_at_sea(self, character):
        """Repair ship using wood from cargo"""
        if self.hull_current >= self.hull_max:
            print("Ship is already at full health!")
            return False

        wood = character.inventory.get('Wood', 0)
        if not isinstance(wood, int) or wood <= 0:
            print("You need wood to repair the ship!")
            return False

        character.inventory['Wood'] = wood - 1
        if character.inventory['Wood'] <= 0:
            del character.inventory['Wood']

        self.hull_current = min(self.hull_current + 15, self.hull_max)
        print(f"Repaired ship hull to {self.hull_current}/{self.hull_max}")
        return True

class TradeShip:
    def __init__(self, home_island, world):
        ship_type = random.choice(list(ship_types.keys()))
        stats = ship_types[ship_type]

        self.type = ship_type
        self.crew = random.randint(5, stats['crew_max'])
        self.speed = stats['speed'] or 1
        self.cargo_capacity = stats['cargo']

        self.home_island = home_island
        self.world = world
        self.current_position = getattr(home_island, 'coordinates', None)
        self.destination = None
        self.days_at_destination = 0
        self.returning_home = False
        self.hold_turns = 0
        self.last_position = self.current_position

        goods = list(trade_goods.keys())
        self.selling = random.choice(goods)
        self.buying = random.choice([g for g in goods if g != self.selling])
        self.sell_price = random.randint(50, 200)
        self.buy_price = random.randint(50, 200)

        if self.current_position is not None:
            self.set_new_destination(world)

    def set_new_destination(self, world):
        """Set a new random destination for the trade ship"""
        if world is None or not getattr(world, 'islands', None):
            return
        available_islands = [island for island in world.islands.values()
                           if island.is_inhabited and island is not self.home_island
                           and getattr(island, 'coordinates', None) is not None]
        if available_islands:
            self.destination = random.choice(available_islands)
            self.returning_home = False
            self.days_at_destination = 0

    def get_position(self):
        """Return current position as tuple for map display"""
        if self.current_position is None:
            return None
        return tuple(self.current_position)

    def _world(self):
        return getattr(self, 'world', None) or getattr(self.home_island, 'world', None)

    def _target(self):
        if self.returning_home:
            return getattr(self.home_island, 'coordinates', None)
        if self.destination is None:
            return None
        return getattr(self.destination, 'coordinates', None)

    def move(self):
        if getattr(self, 'hold_turns', 0) > 0:
            self.hold_turns -= 1
            return
        if self.current_position is None:
            return

        world = self._world()
        if not self.destination and not self.returning_home:
            if world is not None:
                self.set_new_destination(world)
            return

        target = self._target()
        if target is None:
            return

        self.last_position = self.current_position
        x, y = int(self.current_position[0]), int(self.current_position[1])
        target = (int(target[0]), int(target[1]))
        dx = target[0] - x
        dy = target[1] - y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        speed = self.speed or 1

        if distance <= speed:
            self.current_position = target
            home = getattr(self.home_island, 'coordinates', None)
            if self.returning_home and home is not None and target == tuple(home):
                if world is not None:
                    self.set_new_destination(world)
            elif not self.returning_home:
                self.days_at_destination += 1
                if self.days_at_destination >= 3:
                    self.returning_home = True
            return

        move_x = int(dx / distance * speed)
        move_y = int(dy / distance * speed)
        if move_x == 0 and move_y == 0:
            if abs(dx) >= abs(dy) and dx != 0:
                move_x = 1 if dx > 0 else -1
            elif dy != 0:
                move_y = 1 if dy > 0 else -1
        self.current_position = (x + move_x, y + move_y)
