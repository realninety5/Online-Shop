from django.shortcuts import render, redirect, get_object_or_404
import braintree
from django.conf import settings
from orders.models import Order
from .tasks import payment_completed


# Instantiate BrainTree payment gateway
gateway = braintree.BraintreeGateway(settings.BRAINTREE_CONF)

# Create your views here.
def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    total_cost = order.get_total_cost()
    if request.method == 'POST':
        # Get nonce
        nonce = request.POST.get('payment_method_nonce', None)
        # Create and submit a transaction
        result = gateway.transaction.sale({
            'amount': f'{total_cost:.2f}',
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })

        # Check if transactio  was successful
        if result.is_success:
            # If so, mark the order as paid for
            order.paid = True
            # Store the unique transaction ID
            order.braintree_id = result.transaction.id
            order.save()
            # Load asynchronous task
            # payment_completed.delay(order.id)
            return redirect('payment:done')
        else:
            return redirect('payment:canceled')
    else:
        # Generate a token
        client_token = gateway.client_token.generate()
        return render(request, 'payment/process.html',
                      {'order': order,
                       'client_token': client_token})

def payment_done(request):
    return render(request, 'payment/done.html')

def payment_canceled(request):
    return render(request, 'payment/canceled.html')
