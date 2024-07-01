# industrialpartner/context_processors.py

from .utils import calculate_cart_count

def cart_count(request):
    cart = request.session.get('cart', {})
    cart_count = calculate_cart_count(cart)
    return {'cart_count': cart_count}
