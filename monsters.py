import random
from crystalquest.colors import COLORS
from crystalquest.ascii_art import load_ascii_art, display_ascii_art

class SeaMonster:
    def __init__(self, world):
        self.speed = 1
        self.symbol = '∞'
        # Find a valid starting position (water only). Give up rather than
        # spinning forever if the map is somehow all land.
        size = world.map.size
        self.position = (0, 0)
        for _ in range(size * size):
            pos = (random.randint(0, size - 1), random.randint(0, size - 1))
            if not self._is_island(pos, world):
                self.position = pos
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
        if not trade_ships or self.position is None:
            return destroyed
        for ship in trade_ships:
            position = getattr(ship, 'current_position', None)
            if position is None:
                continue
            try:
                same_square = tuple(position) == tuple(self.position)
            except TypeError:
                same_square = False
            if same_square:
                # Load and display monster art when destroying a ship
                monster_art = load_ascii_art('crystalquest/art/monster.jpeg')
                if monster_art:
                    display_ascii_art(monster_art)
                destroyed.append(ship)
        return destroyed 