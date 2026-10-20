from django.db import models
from orders.models import Order



from django.db import models
from orders.models import Order


class Payment(models.Model):

    class PaymentMethod(models.TextChoices):
        RAZORPAY = "razorpay", "Razorpay"
        COD = "cod", "Cash on Delivery"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.RAZORPAY
    )

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )

    # IDs supplied by the payment gateway
    gateway_order_id = models.CharField(
        max_length=100, blank=True, null=True
    )

    transaction_id = models.CharField(
        max_length=100, unique=True, blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment for Order {self.order_id} - {self.status}"
