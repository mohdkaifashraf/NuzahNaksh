from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):

    class StatusChoice(models.TextChoices):
           ORDER_CONFIRMED = 'order confirmed', 'ORDERCONFIRMED'
           PENDING = 'pending', 'PENDING'
           RECIEVE = 'recived', 'RECIEVED'
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(
           max_length=20,
           choices = StatusChoice.choices,
           default=StatusChoice.PENDING
           )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateField(auto_now=True)
    updatedt_at = models.DateField(auto_now=True)

    class Meta:
              db_table = 'orders'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
              db_table = 'order_items'
    
