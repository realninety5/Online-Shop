from django.db import models
from django.urls import reverse
from parler.models import TranslatedFields, TranslatableModel


# Create your models here.

# Category model to store each product
class Category(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(max_length=200, db_index=True),
        slug = models.SlugField(max_length=200, db_index=True, unique=True)
    )
    class Meta:
        # ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category',
                       args=[self.slug])

# Product model to store the details of each product
class Product(TranslatableModel):
    translations = TranslatedFields(
        description = models.TextField(blank=True),
        name = models.CharField(max_length=200, db_index=True),
        slug = models.SlugField(max_length=200, db_index=True)
    )
    category = models.ForeignKey(Category, related_name='products',
                                 on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d',
                              blank=True)
    price = models.DecimalField(max_digits=10,
                                decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Becuase we used parler to translate the name and slug fields
    class Meta:
        # ordering = ('name',)
        # index_together = (('id', 'slug'),)
        pass

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                       args=[self.id, self.slug])

