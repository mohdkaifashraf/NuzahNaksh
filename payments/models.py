from django.db import models
from orders.models import Order



class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        UPI = 'Gpay','Phonepay', 'paytym'


    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payemnt_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.UPI
    )
    transaction_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
