from django.db import models
from django.conf import settings
from products.models import Product


class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now=True)


    class Meta:
        db_table = 'wishlists'


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['wishlist', 'product'],
                name = 'unique_product_per_wishlist'
            )
        ]

        db_table = 'wishlist_items'

