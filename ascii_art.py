from ascii_magic import AsciiArt

def load_ascii_art(image_path):
    """Load and return ASCII art from an image file"""
    try:
        art = AsciiArt.from_image(image_path)
        return art
    except Exception as e:
        print(f"Could not load ASCII art: {e}")
        return None

def display_ascii_art(art):
    """Display ASCII art to terminal"""
    if art:
        art.to_terminal() 