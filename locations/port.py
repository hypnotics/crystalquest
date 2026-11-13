import random
from crystalquest.prompts import ask, ask_positive_int
from crystalquest.ships import TradeShip

class Port:
    def __init__(self):
        self.travel_cost = 200
        self.trade_ships = []  # List of trade ships currently in port
        self.last_spawn = 0  # Days since last trade ship spawn
        self.home_island = None  # Will be set when port is created

    def spawn_trade_ship(self, current_day, home_island, town_name, world, force=False):
        """Spawn a new trade ship if conditions are met.

        An empty harbor can receive a ship on the first day. Passing force
        guarantees one ship so a new captain can sign on as deckhand.
        """
        if self.home_island is None:
            self.home_island = home_island

        if getattr(home_island, 'coordinates', None) is None:
            return None

        total_trade_ships = 0
        for island in world.islands.values():
            if island.is_inhabited:
                for town in island.towns.values():
                    port = town.locations.get('port')
                    if port:
                        total_trade_ships += len(port.trade_ships)

        if not force and total_trade_ships >= getattr(world, 'max_trade_ships', 1):
            return None
        if not force and self.trade_ships and current_day - self.last_spawn < 2:
            return None
        if not force and random.random() > (0.55 if not self.trade_ships else 0.35):
            return None

        new_ship = TradeShip(self.home_island, world)
        if not new_ship.destination:
            return None

        # Stay in port through the rest of this day so the player can board.
        new_ship.hold_turns = 1
        self.trade_ships.append(new_ship)
        self.last_spawn = current_day
        print(f"A {new_ship.type} is loading at {town_name}, {self.home_island.name}, "
              f"with crew of {new_ship.crew}, headed to {new_ship.destination.name}.")
        return new_ship

    def update_trade_ships(self, trade_ships):
        """Update port's trade ships list"""
        if trade_ships is None:
            trade_ships = []
        self.trade_ships = [ship for ship in self.trade_ships if ship in trade_ships]
        home = getattr(self.home_island, 'coordinates', None) if self.home_island else None
        if home is None:
            return
        for ship in trade_ships:
            position = getattr(ship, 'current_position', None)
            if (position is not None and tuple(position) == tuple(home) and
                    getattr(ship, 'home_island', None) is self.home_island and
                    ship not in self.trade_ships):
                self.trade_ships.append(ship)

    def ships_here(self, trade_ships=None):
        """Ships physically docked at this harbor, still sailing the world."""
        home = getattr(self.home_island, 'coordinates', None) if self.home_island else None
        if home is None:
            return []
        pool = self.trade_ships if trade_ships is None else trade_ships
        docked = []
        for ship in pool:
            position = getattr(ship, 'current_position', None)
            if getattr(ship, 'home_island', None) is not self.home_island:
                continue
            if position is None or tuple(position) != tuple(home):
                continue
            if ship not in docked:
                docked.append(ship)
        return docked

    def handle_trade(self, character, day, trade_ships=None):
        docked = self.ships_here(trade_ships)
        if not docked:
            print("No trade ships in port!")
            return None, None, None, day

        print("\n=== Trading Ships in Port ===")
        for i, ship in enumerate(docked, 1):
            print(f"{i}. {ship.type} - Selling {ship.selling} for {ship.sell_price}, "
                  f"Buying {ship.buying} for {ship.buy_price}")

        try:
            choice = int(ask("\nWhich ship would you like to trade with? (number or 0 to cancel): "))
            if choice == 0:
                return None, None, None, day
            ship = docked[choice - 1]
        except (ValueError, IndexError):
            print("Invalid choice!")
            return None, None, None, day

        print(f"\nTrading with {ship.type}")
        print(f"1. Buy {ship.selling} for {ship.sell_price} gold")
        print(f"2. Sell {ship.buying} for {ship.buy_price} gold")

        trade_choice = ask("What would you like to do? ").strip()

        if trade_choice == "1":
            amount = ask_positive_int("How many would you like to buy? ")
            if amount is None:
                return None, None, None, day
            total_cost = amount * ship.sell_price
            if character.gold >= total_cost:
                character.gold -= total_cost
                character.inventory[ship.selling] = character.inventory.get(ship.selling, 0) + amount
                print(f"You bought {amount} {ship.selling}!")
            else:
                print("You can't afford that!")

        elif trade_choice == "2":
            held = character.inventory.get(ship.buying, 0)
            if not isinstance(held, int) or held <= 0:
                print(f"You don't have any {ship.buying} to sell!")
                return None, None, None, day

            amount = ask_positive_int("How many would you like to sell? ")
            if amount is None:
                return None, None, None, day
            if amount <= held:
                total_payment = amount * ship.buy_price
                character.gold += total_payment
                character.inventory[ship.buying] = held - amount
                if character.inventory[ship.buying] <= 0:
                    del character.inventory[ship.buying]
                print(f"You sold {amount} {ship.buying} for {total_payment} gold!")
            else:
                print(f"You don't have that many {ship.buying}!")
        else:
            print("Invalid choice!")

        return None, None, None, day

    def handle_deckhand_travel(self, day, trade_ships=None):
        available_ships = [ship for ship in self.ships_here(trade_ships) if ship.destination is not None]

        if not available_ships:
            print("No ships currently available for travel!")
            return None, None, None, day

        print("\nAvailable ships:")
        for i, ship in enumerate(available_ships, 1):
            dest = "returning home" if ship.returning_home else f"headed to {ship.destination.name}"
            print(f"{i}. {ship.type} ({dest})")

        choice = ask("\nWhich ship would you like to join? (number or 'cancel'): ").strip()
        if choice.lower() == 'cancel' or choice == '':
            return None, None, None, day

        try:
            chosen_ship = available_ships[int(choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice!")
            return None, None, None, day

        print(f"\nYou've joined the crew of the {chosen_ship.type}!")
        destination = chosen_ship.home_island if chosen_ship.returning_home else chosen_ship.destination
        return destination, None, chosen_ship, day

    def handle_sailing(self, character, world, current_island, day, trade_ships):
        if character.ship is None:
            print("You have no ship to sail.")
            return current_island, None, None, day
        if getattr(current_island, 'coordinates', None) is None:
            print("The harbor mouth is closed. You cannot set sail from here.")
            return current_island, None, None, day
        if not getattr(character.ship, 'is_mobile', lambda: True)():
            print("Your hull is too badly damaged to leave the dock.")
            return current_island, None, None, day

        if trade_ships is None:
            trade_ships = []

        def show_sailing_info(current_day, moves_left):
            print(f"\n=== Day {current_day} ===")
            print("\nUse numpad to navigate:")
            print("7 8 9")
            print("4 5 6")
            print("1 2 3")
            print("(5 to wait, 0 to quit sailing)")
            print(f"\nMoves remaining this day: {moves_left}")

        ship_pos = [int(current_island.coordinates[0]), int(current_island.coordinates[1])]
        moves_remaining = getattr(character.ship, 'speed', 1) or 1
        nemesis = getattr(character, 'nemesis', None)

        while True:
            show_sailing_info(day, moves_remaining)
            world.map.display(
                tuple(ship_pos),
                [(ship.current_position, getattr(ship, 'type', 'Ship'), False)
                 for ship in trade_ships if getattr(ship, 'current_position', None) is not None],
                world.sea_monster,
                day,
                nemesis
            )

            move = ask("Enter direction (0-9): ").strip()
            moves = {
                '8': (-1, 0),   # North
                '2': (1, 0),    # South
                '6': (0, 1),    # East
                '4': (0, -1),   # West
                '7': (-1, -1),  # Northwest
                '9': (-1, 1),   # Northeast
                '1': (1, -1),   # Southwest
                '3': (1, 1),    # Southeast
                '5': (0, 0),    # Wait
                '0': None       # Quit
            }

            if move not in moves:
                print("Invalid direction!")
                continue

            if move == '0':
                return current_island, None, None, day

            if move == '5':
                print("Waiting...")
                day += 1
                moves_remaining = getattr(character.ship, 'speed', 1) or 1
                for ship in trade_ships:
                    ship.move()
                world.sea_monster.move(world)
                if nemesis is not None and hasattr(nemesis, 'pursue'):
                    nemesis.pursue(world, tuple(ship_pos), day, character, steps=1)
                continue

            if moves_remaining <= 0:
                print("No more moves today! Use 5 to wait for next day.")
                continue

            dx, dy = moves[move]
            new_x = ship_pos[0] + dx
            new_y = ship_pos[1] + dy

            if not (0 <= new_x < world.map.size and 0 <= new_y < world.map.size):
                print("You can't sail off the edge of the map!")
                continue

            ship_pos = [new_x, new_y]
            character.ship.position = tuple(ship_pos)
            moves_remaining -= 1

            for ship in trade_ships:
                ship.move()
            world.sea_monster.move(world)
            if nemesis is not None and hasattr(nemesis, 'pursue'):
                nemesis.pursue(world, tuple(ship_pos), day, character, steps=1)

            island_here = world.map.grid[new_x][new_y]
            if island_here:
                print(f"\nYou've reached {island_here.name}!")
                disembark = ask("Would you like to disembark? (yes/no): ").strip().lower()
                if disembark == 'yes':
                    return island_here, None, None, day

    def calculate_distance(self, start, end):
        """Calculate distance between two points using Pythagorean theorem"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        return (dx**2 + dy**2)**0.5

    def calculate_travel_time(self, distance, speed):
        """Calculate travel time based on distance and ship speed"""
        if not speed:
            return 1
        return max(1, int(distance / speed))

    def visit(self, character, world, current_island, day, trade_ships=None):
        print("\n=== Welcome to the Port ===")
        if character.ship:
            print("1. Set Sail")
            print("2. Trade with Ships")
            print("3. Back")
        else:
            print("1. Travel as Deckhand")
            print("2. Trade with Ships")
            print("3. Back")

        choice = ask("What would you like to do? ").strip()

        if character.ship and choice == "1":
            return self.handle_sailing(character, world, current_island, day, trade_ships)
        elif not character.ship and choice == "1":
            return self.handle_deckhand_travel(day, trade_ships)
        elif choice == "2":
            return self.handle_trade(character, day, trade_ships)

        return current_island, None, None, day
