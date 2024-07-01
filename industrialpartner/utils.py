# industrialpartner/utils.py

def calculate_cart_count(cart):
    total_count = 0
    for item_id, item_data in cart.items():
        total_count += item_data['quantity']
    return total_count
