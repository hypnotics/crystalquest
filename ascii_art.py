from pathlib import Path

try:
    from ascii_magic import AsciiArt
except ImportError:
    AsciiArt = None

def load_ascii_art(image_path):
    """Load and return ASCII art from an image file."""
    if AsciiArt is None:
        return None
    path = Path(image_path)
    if not path.is_file():
        path = Path(__file__).resolve().parent / "art" / Path(image_path).name
    try:
        return AsciiArt.from_image(str(path))
    except Exception as e:
        print(f"Could not load ASCII art: {e}")
        return None

def display_ascii_art(art):
    """Display ASCII art to terminal."""
    if art:
        try:
            art.to_terminal()
        except Exception as e:
            print(f"Could not display ASCII art: {e}")
