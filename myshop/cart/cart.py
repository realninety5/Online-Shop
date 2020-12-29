from decimal import Decimal
from django.conf import settings
from shop.models import Product
from coupons.models import Coupon

class Cart(object):
    def __init__(self, request):
        # Set up the cart
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Save an empty dict in the session for this request
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # Stores current applied coupon
        self.coupon_id = self.session.get('coupon_id')

    # Add a product to the cart
    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}

        # If new quantity, update the quantity
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    # Save session by marking it as 'modified'
    def save(self):
        self.session.modified = True

    # Method to remove product from cart
    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    # Method to get products in cart from the DB
    def __iter__(self):
        product_ids = self.cart.keys()

        # Filter the products from the DB
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        # update the product in the cart
        for product in products:
            cart[str(product.id)]['product'] = product

        # Return a list of items in the cart after updating
        # their price and total price
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    # Returns the total number of products in Cart
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    # Returns the total price of all products in cart
    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] \
                   for item in self.cart.values())

    # Clear cart of products
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    # Checks if the coupon is valid, if so, retrieve it
    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    # If coupon is valid, get its discount and apply it
    def get_discount(self):
        if self.coupon():
            return (self.coupon.discount / Decimal(100)) \
                    * self.get_total_price()
        return Decimal(0)

    # Return the total price after the discount has been applied
    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
