from django.shortcuts import render, get_object_or_404
from cart.forms import CartAddProductForm
from cart.forms import CartAddProductForm
from .models import Category, Product
from .recommender import Recommender

# Create your views here.


def product_list(request, category_slug=None):
    language = request.LANGUAGE_CODE
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    # If category_spug was passed, return the products in the given category
    # Else, return all products; that is, in all categories
    if category_slug:
        category = get_object_or_404(Category,
                                     translations__language_code=language,
                                     translations__slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'shop/product/list.html',
                  {'category': category,
                   'categories': categories,
                   'products': products})


# Retrieve and return a given product
def product_detail(request, id, slug):
    language = request.LANGUAGE_CODE
    product = get_object_or_404(Product, id=id,
                                translations__language_code=language,
                                translations__slug=slug,
                                available=True)
    cart_product_form = CartAddProductForm()
    r = Recommender()
    recommended_products = r.suggest_product_for([product], 4)
    return render(request, 'shop/product/detail.html',
                  {'product': product,
                   'cart_product_form': cart_product_form,
                   'recommended_products': recommended_products})
