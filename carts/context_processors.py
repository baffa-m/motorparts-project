from .models import Cart

def cart_context(request):
    cart = None
    cart_total = 0
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_key=session_key).first()
    
    if cart:
        cart_total = cart.get_total_items()
    
    return {
        'cart': cart,
        'cart_total_items': cart_total,
    }