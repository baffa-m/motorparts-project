from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from orders.models import Order
from .models import Payment, BankAccount
import json
from datetime import datetime
import uuid
from django.urls import reverse
import requests


@login_required
def initiate_payment(request, order_id):
    """
    Initiate Paystack payment for an order using popup
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'completed':
        messages.info(request, 'This order has already been paid for.')
        return redirect('orders:detail', pk=order.id)
    
    # Generate unique payment reference
    reference = f"PAY-{order.order_number}-{uuid.uuid4().hex[:8].upper()}"
    
    # Create payment record
    payment = Payment.objects.create(
        order=order,
        reference=reference,
        amount=order.total_amount,
        payment_method='paystack',
        status='pending'
    )
    
    # Paystack configuration
    paystack_public_key = getattr(settings, 'PAYSTACK_PUBLIC_KEY', 'pk_test_xxxxxxxxxxxxx')
    
    # Convert amount to kobo (Paystack uses kobo for NGN)
    amount_in_kobo = int(float(order.total_amount) * 100)
    callback_url = request.build_absolute_uri(
        reverse('payment:verify', args=[reference])
    )
    context = {
        'order': order,
        'payment': payment,
        'paystack_public_key': paystack_public_key,
        'amount_in_kobo': amount_in_kobo,
        'email': request.user.email,
        'reference': reference,
        'callback_url': callback_url,

    }
    
    return render(request, 'payment/initiate.html', context)

@login_required
def bank_transfer_payment(request, order_id):
    """
    Show bank transfer details for payment
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'completed':
        messages.info(request, 'This order has already been paid for.')
        return redirect('orders:detail', pk=order.id)
    
    # Create payment record
    reference = f"BANK-{order.order_number}-{uuid.uuid4().hex[:8].upper()}"
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'reference': reference,
            'amount': order.total_amount,
            'payment_method': 'bank_transfer',
            'status': 'pending'
        }
    )
    
    # Bank details (replace with actual bank details)
    bank_details = {
        'bank_name': 'First Bank of Nigeria',
        'account_name': 'MotorParts Pro Limited',
        'account_number': '1234567890',
        'sort_code': '011',
    }
    
    context = {
        'order': order,
        'payment': payment,
        'bank_details': bank_details,
    }
    
    return render(request, 'payment/bank_transfer.html', context)

@login_required
def confirm_transfer(request, order_id):
    """
    User confirms they have made the bank transfer
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        # Update order status to awaiting confirmation
        order.status = 'pending'
        order.payment_status = 'pending'
        order.save()
        
        # Update payment status
        payment = Payment.objects.filter(order=order).first()
        if payment:
            payment.status = 'pending'
            payment.save()
        
        messages.success(request, 'Transfer confirmation received! Your order will be processed once admin confirms the payment.')
        return redirect('orders:detail', pk=order.id)
    
    return redirect('payment:bank_transfer', order_id=order_id)

@csrf_exempt
def payment_callback(request):
    """
    Handle Paystack payment callback/webhook
    """
    if request.method == 'POST':
        try:
            # Get Paystack signature for verification
            paystack_signature = request.headers.get('x-paystack-signature', '')
            
            # Parse payment data
            payload = request.body
            data = json.loads(payload)
            
            event = data.get('event')
            event_data = data.get('data', {})
            
            if event == 'charge.success':
                reference = event_data.get('reference')
                status = event_data.get('status')
                
                if status == 'success':
                    # Find payment by reference
                    try:
                        payment = Payment.objects.get(reference=reference)
                        
                        # Update payment status
                        payment.status = 'completed'
                        payment.transaction_id = event_data.get('id')
                        payment.gateway_response = event_data
                        payment.paid_at = datetime.now()
                        payment.save()
                        
                        # Update order status
                        order = payment.order
                        order.payment_status = 'completed'
                        order.status = 'paid'
                        order.payment_method = 'paystack'
                        order.save()
                        
                        return JsonResponse({'status': 'success'})
                    except Payment.DoesNotExist:
                        return JsonResponse({'status': 'payment_not_found'}, status=404)
            
            return JsonResponse({'status': 'event_received'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'invalid_request'}, status=400)

@login_required
def verify_payment(request, reference):
    """
    Verify payment status with Paystack
    """
    try:
        payment = get_object_or_404(Payment, reference=reference, order__user=request.user)
        
        # Verify with Paystack API
        paystack_secret_key = getattr(settings, 'PAYSTACK_SECRET_KEY', 'sk_test_xxxxxxxxxxxxx')
        
        headers = {
            'Authorization': f'Bearer {paystack_secret_key}',
            'Content-Type': 'application/json',
        }
        
        response = requests.get(
            f'https://api.paystack.co/transaction/verify/{reference}',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') and data['data'].get('status') == 'success':
                # Update payment
                payment.status = 'completed'
                payment.transaction_id = data['data'].get('id')
                payment.gateway_response = data['data']
                payment.paid_at = datetime.now()
                payment.save()
                
                # Update order
                order = payment.order
                order.payment_status = 'completed'
                order.status = 'paid'
                order.payment_method = 'paystack'
                order.save()
                
                messages.success(request, 'Payment verified successfully!')
                return redirect('orders:success', pk=order.id)
            else:
                payment.status = 'failed'
                payment.gateway_response = data
                payment.save()
                messages.error(request, 'Payment verification failed.')
                return redirect('payment:failed', order_id=payment.order.id)
        else:
            messages.error(request, 'Unable to verify payment. Please contact support.')
            return redirect('orders:detail', pk=payment.order.id)
            
    except Exception as e:
        messages.error(request, f'Error verifying payment: {str(e)}')
        return redirect('orders:list')

@login_required
def payment_success(request, order_id):
    """Display payment success page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return redirect('orders:success', pk=order.id)

@login_required
def payment_failed(request, order_id):
    """Display payment failed page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    messages.error(request, 'Payment failed. Please try again.')
    return redirect('orders:detail', pk=order.id)


@login_required
def bank_transfer_payment(request, order_id):
    """Show bank transfer details for payment"""
    print('here')
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'completed':
        messages.info(request, 'This order has already been paid for.')
        return redirect('orders:detail', pk=order.id)
    
    # Create payment record
    reference = f"BANK-{order.order_number}-{uuid.uuid4().hex[:8].upper()}"
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'reference': reference,
            'amount': order.total_amount,
            'payment_method': 'bank_transfer',
            'status': 'pending'
        }
    )
    
    # Get active bank accounts from database
    bank_accounts = BankAccount.objects.filter(is_active=True)
    
    context = {
        'order': order,
        'payment': payment,
        'bank_accounts': bank_accounts,
    }
    
    return render(request, 'payment/bank_transfer.html', context)

@login_required
def confirm_transfer(request, order_id):
    """User confirms they have made the bank transfer"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        # Update order status to awaiting confirmation
        order.status = 'pending'
        order.payment_status = 'pending'
        order.save()
        
        # Update payment status
        payment = Payment.objects.filter(order=order).first()
        if payment:
            payment.status = 'pending'
            payment.save()
        
        messages.success(request, 'Transfer confirmation received! Your order will be processed once we confirm the payment.')
        return redirect('orders:detail', pk=order.id)
    
    return redirect('payment:bank_transfer', order_id=order_id)