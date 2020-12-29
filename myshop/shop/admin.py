from django.contrib import admin
from .models import Category, Product
from parler.admin import TranslatableAdmin

# Register your models here.

# Reg and create Admin interative interface for Category
@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ('name', 'slug')
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}

# Reg and create Admin interative interface for Product
@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = ('name', 'slug', 'price', 'available',
                    'created', 'updated')
    list_filter = ('available', 'created', 'updated')
    list_editable = ('price', 'available')
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}
