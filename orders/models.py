from django.db import models
from django.conf import settings
from products.models import Product



class Order(models.Model):

    class StatusChoice(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    # A snapshot of the delivery address at checkout
    delivery_address = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=StatusChoice.choices,
        default=StatusChoice.PENDING
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_charge = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.pk} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="items"
    )

    product = models.ForeignKey(
        "products.Product",  # Change if your Product model is in another app
        on_delete=models.PROTECT
    )

    # Snapshot of the product name when purchased
    product_name = models.CharField(max_length=255)

    quantity = models.PositiveIntegerField()

    # Price per unit at the time of purchase
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Total discount for this line item
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_items"

    @property
    def line_total(self):
        return (self.unit_price * self.quantity) - self.discount

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"