from django.core.exceptions import ObjectDoesNotExist
from .models import CartItem, Cart

def cartitem_counter(request):
    if not request.user.is_authenticated:
        return 0
    
    try:
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = CartItem.objects.filter(cart=cart)
        total_item = sum(item.quantity for item in cart_items)
        return total_item
    
    except (ObjectDoesNotExist, Cart.DoesNotExist):
        return 0
    
def cart_context(request):
    return {
        'count_cart' : cartitem_counter(request)
    }