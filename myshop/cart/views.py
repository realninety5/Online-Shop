from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from coupons.forms import CouponApplyForm
from shop.recommender import Recommender

# Create your views here.

# Only requests with "POST" method
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    # Check if form is valid
    if form.is_valid():
        cd = form.cleaned_data
        # Add item(s) to the cart
        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])

    return redirect('cart:cart_detail')

# Only requests with "POST" method
@require_POST
# Removes items from the cart
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


# Update the cart with the new quantity
def cart_detail(request):
    cart = Cart(request)
    # For each item, instantiate item with CartAddProductForm 
    # with the given quantity
    # and override set to True
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'], 'override': True})
    coupon_apply_form = CouponApplyForm()
    r = Recommender()
    cart_products = [item['product'] for item in cart]
    recommended_products = r.suggest_product_for(cart_products,
                                                 max_results=4)
    return render(request, 'cart/detail.html', {'cart': cart,
                                'coupon_apply_form': coupon_apply_form,
                                'recommended_products': recommended_products})
