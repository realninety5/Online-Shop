from django import forms
from django.utils.translation import gettext_lazy as _

# Limit the choice to 21
PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]

class CartAddProductForm(forms.Form):
    # Specifies the number of each item to add to the cart
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES,
                                     coerce=int,
                                     label=_('Quantity'))
    # Choose to override existing items in the cart
    override = forms.BooleanField(required=False,
                                  initial=False,
                                  widget=forms.HiddenInput)
