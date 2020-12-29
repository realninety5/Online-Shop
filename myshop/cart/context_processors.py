from .cart import Cart

# Makes the cart available to all templates in the project
def cart(request):
    return {'cart': Cart(request)}
