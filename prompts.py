def ask(prompt=""):
    """Read a line of input. Leaving the game with Ctrl-D or Ctrl-C exits cleanly."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\nThanks for playing!")
        raise SystemExit(0)


def ask_positive_int(prompt):
    """Return a whole number greater than zero, or None when the answer is unusable."""
    try:
        amount = int(ask(prompt).strip())
    except ValueError:
        print("Please enter a valid number!")
        return None
    if amount <= 0:
        print("Please enter a positive number!")
        return None
    return amount
