from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from .tasks import order_created
from django.urls import reverse
from django.shortcuts import render, redirect
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint

# Create your views here.

def order_create(request):
    cart = Cart(request)
    # If POST, if form is_valid (and coupon, get the discount) 
    # and save the order to the DB 
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon():
                order.coupon = cart.coupon()
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])

                # Empty the cart
            cart.clear()
            # Launch asynchronous tast
            order_created.delay(order.id)
            # Set the order in the session
            request.session['order_id'] = order.id
            # Redirect for payment
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html',
                  {'cart': cart, 'form': form})


# Get an order object and return it to the admin page
@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html',
                  {'order': order})


# Allows to staff to create a pdf-receipt for a particular order
@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(response,
                                           stylesheet=[weasyprint.CSS(
                                               settings.STATIC_ROOT + 'css/pdf.css')])
    return response

