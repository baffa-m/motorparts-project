from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from decimal import Decimal
from .models import Order, OrderItem
from carts.views import get_or_create_cart
from shipping.models import ShippingMethod

@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('part').all()
    
    if not cart_items:
        messages.error(request, 'Your cart is empty')
        return redirect('carts:detail')
    
    # Check stock availability
    for item in cart_items:
        if item.quantity > item.part.stock_quantity:
            messages.error(request, f'{item.part.name} has insufficient stock')
            return redirect('carts:detail')
    
    subtotal = cart.get_total_price()
    
    shipping_methods = ShippingMethod.objects.filter(is_active=True)
    
    shipping_amount = Decimal('2000.00')  # Default flat rate
    if shipping_methods.exists():
        shipping_amount = shipping_methods.first().base_cost
    
    total_amount = subtotal + shipping_amount
    
    # Get user profile for pre-filling address
    user_profile = None
    if hasattr(request.user, 'profile'):
        user_profile = request.user.profile
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_amount': shipping_amount,
        'shipping_methods': shipping_methods,
        'total_amount': total_amount,
        'user_profile': user_profile,
    }
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'paystack')
        
        shipping_method_id = request.POST.get('shipping_method')
        if shipping_method_id:
            try:
                shipping_method = ShippingMethod.objects.get(id=shipping_method_id, is_active=True)
                shipping_amount = shipping_method.base_cost
            except ShippingMethod.DoesNotExist:
                messages.error(request, 'Invalid shipping method selected')
                return redirect('orders:checkout')
        
        total_amount = subtotal + shipping_amount
        
        # Check if user wants to use profile address
        use_profile_address = request.POST.get('use_profile_address') == 'on'
        
        if use_profile_address and user_profile:
            shipping_address = user_profile.address
            shipping_city = user_profile.city
            shipping_state = user_profile.state
            shipping_postal_code = user_profile.postal_code
        else:
            shipping_address = request.POST.get('address')
            shipping_city = request.POST.get('city')
            shipping_state = request.POST.get('state')
            shipping_postal_code = request.POST.get('postal_code')
        
        try:
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    subtotal=subtotal,
                    shipping_amount=shipping_amount,
                    total_amount=total_amount,
                    shipping_first_name=request.POST.get('first_name'),
                    shipping_last_name=request.POST.get('last_name'),
                    shipping_address=shipping_address,
                    shipping_city=shipping_city,
                    shipping_state=shipping_state,
                    shipping_postal_code=shipping_postal_code,
                    shipping_phone=request.POST.get('phone'),
                    payment_method=payment_method,
                )
                
                # Create order items and update stock
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        part=item.part,
                        quantity=item.quantity,
                        unit_price=item.part.price.amount,
                        total_price=item.get_total_price(),
                    )
                    
                    # Update stock
                    item.part.stock_quantity -= item.quantity
                    item.part.save()
                
                # Clear cart
                cart.items.all().delete()
                
                messages.success(request, f'Order {order.order_number} created successfully!')
                
                # Redirect based on payment method
                if payment_method == 'paystack':
                    return redirect('payment:initiate', order_id=order.id)
                elif payment_method == 'bank_transfer':
                    return redirect('payment:bank_transfer', order_id=order.id)
                else:  # cash_on_delivery
                    order.status = 'processing'
                    order.save()
                    return redirect('orders:success', pk=order.id)
                
        except Exception as e:
            messages.error(request, f'Error processing order: {str(e)}')
            return redirect('carts:detail')
    
    return render(request, 'orders/checkout.html', context)

@login_required
def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__part')
