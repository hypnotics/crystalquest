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

# Define color class with fallback symbols
class Colors:
    def __init__(self):
        self.use_colors = supports_color()
        
        if self.use_colors:
            self.BLUE = '\033[94m'      # Light blue for water
            self.GREEN = '\033[92m'     # Green for inhabited islands
            self.YELLOW = '\033[93m'    # Yellow for uninhabited islands
            self.RED = '\033[91m'       # Red for ships
            self.WHITE = '\033[97m'     # White for player
            self.GRAY = '\033[90m'      # Gray for sea monster
            self.RESET = '\033[0m'      # Reset color
        else:
            # Fallback ASCII symbols
            self.BLUE = ''
            self.GREEN = ''
            self.YELLOW = ''
            self.RED = ''
            self.WHITE = ''
            self.GRAY = ''
            self.RESET = ''
    
    def colorize(self, text, color):
        """Apply color to text with fallback symbols"""
        if self.use_colors:
            return f"{color}{text}{self.RESET}"
        else:
            # Fallback symbols when colors aren't supported
            symbols = {
                self.BLUE: '~',    # water
                self.GREEN: '#',   # inhabited islands
                self.YELLOW: 'o',  # uninhabited islands
                self.RED: 'S',     # ships
                self.WHITE: '@',   # player
                self.GRAY: '8',    # sea monster
            }
            return symbols.get(color, text)

# Create a global instance
COLORS = Colors() 