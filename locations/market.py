from crystalquest.items import trade_goods
from crystalquest.prompts import ask, ask_positive_int

class Market:
    def __init__(self):
        self.goods = trade_goods

    def visit(self, character):
        print("\n=== Welcome to the Market ===")
        print("Available goods:")

        goods_list = list(self.goods.items())
        for i, (item_name, item_data) in enumerate(goods_list, 1):
            print(f"{i}. {item_data['description']} - {item_data['price']} gold")

        choice = ask("\nWhat would you like to buy? (number or 'cancel'): ").strip()
        if choice.lower() == 'cancel' or choice == '':
            return

        try:
            index = int(choice) - 1
        except ValueError:
            print("Please enter a valid number!")
            return

        if not (0 <= index < len(goods_list)):
            print("Invalid choice!")
            return

        item_name, item_data = goods_list[index]
        amount = ask_positive_int("How many would you like to buy? ")
        if amount is None:
            return

        price = item_data.get('price', 0)
        total_cost = amount * price
        if character.gold < total_cost:
            print("You can't afford that many!")
            return

        character.gold -= total_cost
        character.inventory[item_name] = character.inventory.get(item_name, 0) + amount
        print(f"You bought {amount} {item_name}!")
