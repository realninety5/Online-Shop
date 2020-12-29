import redis
from django.conf import settings
from .models import Product

# Connect to Redis DB
r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)

class Recommender(object):
    def get_product_key(self, id):
        return f'product:{id}:purchased_with'

    def products_bought(self, products):
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                # Retrieve the other products bought with each products
                if with_id != product_id:
                    r.zincrby(self.get_product_key(product_id), 1, with_id)

    def suggest_product_for(self, products, max_results=6):
        product_ids = [p.id for p in products]
        if len(products) == 1:
            # Only one products
            suggesstions = r.zrange(self.get_product_key(product_ids[0]),
                                    0, -1, desc=True)[:max_results]
        else:
            # Produce a temporary key
            flat_ids = ''.join([str(id) for id in product_ids])
            tmp_key = f'tmp_{flat_ids}'
            # Combine scores of multiple products
            # Store the resulting set in a temp key
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(tmp_key, keys)
            # Remove id for the product which owns the recommendation
            r.zrem(tmp_key, *product_ids)
            # Get the product_ids by their score, descendant sort
            suggesstions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]
            # Remove thw temp key
            r.delete(tmp_key)
        suggessted_product_ids = [int(id) for id in suggesstions]
        # Get suggessted products and sort them by order of appearance
        suggessted_products = list(Product.objects.filter(
            id__in=suggessted_product_ids))
        suggessted_products.sort(key=lambda x:
                                 suggessted_product_ids.index(x.id))
        return suggessted_products

    def clear_purchases(self):
        for id in Product.object.values_list('id', flat=True):
            r.delete(self.get_product_key(id))
