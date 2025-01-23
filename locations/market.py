from crystalquest.items import trade_goods

class Market:
    def __init__(self):
        self.goods = trade_goods

    def visit(self, character):
        print("\n=== Welcome to the Market ===")
        print("Available goods:")
        
        # Create numbered list of goods
        goods_list = list(self.goods.items())
        for i, (item_name, item_data) in enumerate(goods_list, 1):
            print(f"{i}. {item_data['description']} - {item_data['price']} gold")

        choice = input("\nWhat would you like to buy? (number or 'cancel'): ")
        if choice.lower() == 'cancel':
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(goods_list):
                item_name, item_data = goods_list[index]
                amount = input("How many would you like to buy? ")
                try:
                    amount = int(amount)
                    total_cost = amount * item_data['price']
                    if character.gold >= total_cost:
                        character.gold -= total_cost
                        character.inventory[item_name] = character.inventory.get(item_name, 0) + amount
                        print(f"You bought {amount} {item_name}!")
                    else:
                        print("You can't afford that many!")
                except ValueError:
                    print("Please enter a valid number!")
            else:
                print("Invalid choice!")
        except ValueError:
            print("Please enter a valid number!") 