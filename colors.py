import os
import sys

# Check if the terminal supports colors
def supports_color():
    """
    Returns True if the running system's terminal supports color,
    and False otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)
    
    # isatty is not always implemented
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    if not supported_platform or not is_a_tty:
        return False
        
    return True

class COLORS:
    def __init__(self):
        self.use_colors = supports_color()
        
        # ANSI color codes
        self.BLACK = '\033[30m'
        self.RED = '\033[31m'
        self.GREEN = '\033[32m'
        self.YELLOW = '\033[33m'
        self.BLUE = '\033[34m'
        self.MAGENTA = '\033[35m'
        self.CYAN = '\033[36m'
        self.WHITE = '\033[37m'
        self.GRAY = '\033[90m'
        self.RESET = '\033[0m'
        
        # Game-specific colors
        self.WATER = '\033[94m'      # Light blue for water
        self.ISLAND_INHABITED = '\033[92m'     # Green for inhabited islands
        self.ISLAND_UNINHABITED = '\033[93m'    # Yellow for uninhabited islands
        self.SHIP = '\033[91m'       # Red for ships
        self.PLAYER = '\033[97m'     # White for player
        self.MONSTER = '\033[90m'      # Gray for sea monster
        
        if not self.use_colors:
            # Clear color codes only. dir() also lists methods, and wiping those
            # makes colorize unusable in a non-color terminal.
            for attr in list(vars(self)):
                if attr.startswith('_') or attr == 'use_colors':
                    continue
                setattr(self, attr, '')
    
    def colorize(self, text, color):
        """Apply color to text, or return the text unchanged."""
        if self.use_colors and color:
            return f"{color}{text}{self.RESET}"
        return text

# Create a global instance
COLORS = COLORS()

# Export individual colors for convenience
RED = COLORS.RED
RESET = COLORS.RESET
GRAY = COLORS.GRAY 