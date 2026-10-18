from django.db import models
from django.conf import settings
from products.models import Product

class Cart(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at =models.DateField(auto_now=True)
    updated_at =models.DateField(auto_now=True)


    class Meta:
        db_table = 'carts'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=0)
    created_at =models.DateField(auto_now=True)
    updated_at =models.DateField(auto_now=True)

    @property
    def line_total(self):
        return self.product.discounted_price * self.quantity

    @property
    def total(self):
        return self.line_total

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'],
                name = 'unique_product_per_cart'
            )
        ]
        db_table = 'cart_items'