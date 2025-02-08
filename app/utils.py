from django.core.exceptions import ObjectDoesNotExist
from .models import Cart

def cartitem_counter(request):
    if not request.user.is_authenticated:
        return 0
    
    try:
        cart = Cart.objects.get(user=request.user)
        return cart.cartitem_set.count()
    
    except ObjectDoesNotExist:
        return 0
    
def cart_context(request):
    return {
        'count_cart' : cartitem_counter(request)
    }