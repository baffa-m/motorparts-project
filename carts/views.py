from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.views.generic import DetailView, View
from .models import Cart, CartItem
from parts.models import Part

def get_or_create_cart(request):
    """Helper function to get or create cart for user/session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

class CartDetailView(DetailView):
    model = Cart
    template_name = 'carts/cart_detail.html'
    context_object_name = 'cart'
    
    def get_object(self):
        return get_or_create_cart(self.request)

@require_POST
def add_to_cart(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        messages.error(request, 'Invalid quantity')
        return redirect('parts:detail', pk=part_id)
    
    if part.stock_quantity < quantity:
        messages.error(request, f'Only {part.stock_quantity} items available in stock')
        return redirect('parts:detail', pk=part_id)
    
    cart = get_or_create_cart(request)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        part=part,
        defaults={'quantity': quantity}
    )
    
    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > part.stock_quantity:
            messages.error(request, f'Cannot add more. Only {part.stock_quantity} items available')
            return redirect('carts:detail')
        cart_item.quantity = new_quantity
        cart_item.save()
    
    messages.success(request, f'{part.name} added to cart!')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.get_total_items(),
            'message': f'{part.name} added to cart!'
        })
    
    return redirect('carts:detail')

@require_POST
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    
    if cart_item.cart != cart:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Invalid cart item'})
        messages.error(request, 'Invalid cart item')
        return redirect('carts:detail')
    
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        message = 'Item removed from cart'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': message, 'removed': True})
        messages.success(request, message)
    elif quantity > cart_item.part.stock_quantity:
        message = f'Only {cart_item.part.stock_quantity} items available'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': message})
        messages.error(request, message)
    else:
        cart_item.quantity = quantity
        cart_item.save()
        message = 'Cart updated'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': message,
                'item_total': float(cart_item.get_total_price()),
                'cart_total': float(cart.get_total_price())
            })
        messages.success(request, message)
    
    return redirect('carts:detail')

@require_POST
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    
    if cart_item.cart != cart:
        messages.error(request, 'Invalid cart item')
        return redirect('carts:detail')
    
    part_name = cart_item.part.name
    cart_item.delete()
    messages.success(request, f'{part_name} removed from cart')
    
    return redirect('carts:detail')

def clear_cart(request):
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    messages.success(request, 'Cart cleared')
    return redirect('carts:detail')

def cart_count(request):
    """Return cart item count as JSON"""
    cart = get_or_create_cart(request)
    count = cart.get_total_items()
    return JsonResponse({'count': count})
