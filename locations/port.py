import random
from crystalquest.ships import TradeShip

class Port:
    def __init__(self):
        self.travel_cost = 200
        self.trade_ships = []  # List of trade ships currently in port
        self.last_spawn = 0  # Days since last trade ship spawn
        self.home_island = None  # Will be set when port is created

    def spawn_trade_ship(self, current_day, home_island, town_name, world):
        """Spawn a new trade ship if conditions are met"""
        # Set home island if not already set
        if self.home_island is None:
            self.home_island = home_island
        
        # Count total trade ships in the world
        total_trade_ships = 0
        for island in world.islands.values():
            if island.is_inhabited:
                for town in island.towns.values():
                    if 'port' in town.locations:
                        total_trade_ships += len(town.locations['port'].trade_ships)
        
        # Only spawn if below max limit and enough time has passed
        if (total_trade_ships < world.max_trade_ships and 
            current_day - self.last_spawn >= random.randint(3, 7)):
            new_ship = TradeShip(self.home_island, world)
            if new_ship.destination:  # Only add ship if it has a valid destination
                self.trade_ships.append(new_ship)
                self.last_spawn = current_day
                print(f"New {new_ship.type} spawned at {town_name}, {self.home_island.name}, "
                      f"headed to {new_ship.destination.name} "
                      f"({total_trade_ships + 1}/{world.max_trade_ships} ships)")
                return new_ship
        else:
            print(f"Trade ship spawn check at {town_name}, {self.home_island.name} "
                  f"({total_trade_ships}/{world.max_trade_ships} ships)")
        return None

    def update_trade_ships(self, trade_ships):
        """Update port's trade ships list"""
        # Remove ships that have left
        self.trade_ships = [ship for ship in self.trade_ships if ship in trade_ships]
        # Add ships that have arrived at this port
        for ship in trade_ships:
            if (ship.current_position == ship.home_island.coordinates and 
                ship.home_island == self.home_island and 
                ship not in self.trade_ships):
                self.trade_ships.append(ship)

    def handle_trade(self, character, day):
        if not self.trade_ships:
            print("No trade ships in port!")
            return None, None, None, day  # Return tuple instead of just day
            
        print("\n=== Trading Ships in Port ===")
        for i, ship in enumerate(self.trade_ships, 1):
            print(f"{i}. {ship.type} - Selling {ship.selling} for {ship.sell_price}, "
                  f"Buying {ship.buying} for {ship.buy_price}")
        
        try:
            choice = int(input("\nWhich ship would you like to trade with? (number or 0 to cancel): "))
            if choice == 0:
                return None, None, None, day  # Return tuple
            
            ship = self.trade_ships[choice - 1]
            print(f"\nTrading with {ship.type}")
            print(f"1. Buy {ship.selling} for {ship.sell_price} gold")
            print(f"2. Sell {ship.buying} for {ship.buy_price} gold")
            
            trade_choice = input("What would you like to do? ")
            
            if trade_choice == "1":
                amount = int(input("How many would you like to buy? "))
                total_cost = amount * ship.sell_price
                if character.gold >= total_cost:
                    character.gold -= total_cost
                    character.inventory[ship.selling] = character.inventory.get(ship.selling, 0) + amount
                    print(f"You bought {amount} {ship.selling}!")
                else:
                    print("You can't afford that!")
                    
            elif trade_choice == "2":
                if ship.buying not in character.inventory:
                    print(f"You don't have any {ship.buying} to sell!")
                    return None, None, None, day  # Return tuple
                    
                amount = int(input("How many would you like to sell? "))
                if amount <= character.inventory[ship.buying]:
                    total_payment = amount * ship.buy_price
                    character.gold += total_payment
                    character.inventory[ship.buying] -= amount
                    if character.inventory[ship.buying] == 0:
                        del character.inventory[ship.buying]
                    print(f"You sold {amount} {ship.buying} for {total_payment} gold!")
                else:
                    print(f"You don't have that many {ship.buying}!")
                    
        except (ValueError, IndexError):
            print("Invalid choice!")
            
        return None, None, None, day  # Return tuple

    def handle_deckhand_travel(self, day):
        # Filter out ships with no destination
        available_ships = [ship for ship in self.trade_ships if ship.destination is not None]
        
        if not available_ships:
            print("No ships currently available for travel!")
            return None, None, None, day

        print("\nAvailable ships:")
        for i, ship in enumerate(available_ships, 1):
            dest = "returning home" if ship.returning_home else f"headed to {ship.destination.name}"
            print(f"{i}. {ship.type} ({dest})")
        
        choice = input("\nWhich ship would you like to join? (number or 'cancel'): ")
        if choice.lower() == 'cancel':
            return None, None, None, day
            
        try:
            chosen_ship = available_ships[int(choice) - 1]
            print(f"\nYou've joined the crew of the {chosen_ship.type}!")
            return ((chosen_ship.destination if not chosen_ship.returning_home 
                    else chosen_ship.home_island), None, chosen_ship, day)
        except (ValueError, IndexError):
            print("Invalid choice!")
            return None, None, None, day

    def handle_sailing(self, character, world, current_island, day):
        print("\nUse numpad to navigate:")
        print("7 8 9")
        print("4 5 6")
        print("1 2 3")
        print("(5 to wait, 0 to quit sailing)")
        
        ship_pos = list(current_island.coordinates)
        moves_remaining = character.ship.speed
        
        while True:
            # Display map with current ship position
            world.map.display(tuple(ship_pos))
            
            print(f"\nMoves remaining this day: {moves_remaining}")
            move = input("Enter direction (0-9): ")
            
            # Movement mapping
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
                moves_remaining = character.ship.speed
                continue
                
            if moves_remaining <= 0:
                print("No more moves today! Use 5 to wait for next day.")
                continue
                
            dx, dy = moves[move]
            new_x = ship_pos[0] + dx
            new_y = ship_pos[1] + dy
            
            # Check if new position is within bounds
            if 0 <= new_x < world.map.size and 0 <= new_y < world.map.size:
                ship_pos = [new_x, new_y]
                moves_remaining -= 1
                
                # Check if we're on an island
                island_here = world.map.grid[new_x][new_y]
                if island_here:
                    print(f"\nYou've reached {island_here.name}!")
                    disembark = input("Would you like to disembark? (yes/no): ").lower()
                    if disembark == 'yes':
                        return island_here, None, None, day
            else:
                print("You can't sail off the edge of the map!")

        return current_island, None, None, day

    def calculate_distance(self, start, end):
        """Calculate distance between two points using Pythagorean theorem"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        return (dx**2 + dy**2)**0.5

    def calculate_travel_time(self, distance, speed):
        """Calculate travel time based on distance and ship speed"""
        return max(1, int(distance / speed))

    def visit(self, character, world, current_island, day):
        print("\n=== Welcome to the Port ===")
        if character.ship:
            print("1. Set Sail")
            print("2. Trade with Ships")
            print("3. Back")
        else:
            print("1. Travel as Deckhand")
            print("2. Trade with Ships")
            print("3. Back")
        
        choice = input("What would you like to do? ")
        
        if character.ship and choice == "1":
            return self.handle_sailing(character, world, current_island, day)
        elif not character.ship and choice == "1":
            return self.handle_deckhand_travel(day)
        elif choice == "2":
            return self.handle_trade(character, day)
        
        return current_island, None, None, day