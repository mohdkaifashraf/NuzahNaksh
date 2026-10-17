from django.db import models
from django.db.models import CASCADE
from decimal import Decimal

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True, blank=False)
    category_description = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.category_name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, blank=False)
    product_name = models.CharField(max_length=50, blank=False)
    product_description = models.TextField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    discount_percentage = models.IntegerField(default= 0)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    @property
    def discounted_price(self):
        discount = Decimal(self.discount_percentage)
        result = self.price * (Decimal("100") - discount) / Decimal("100")
        return result.quantize(Decimal("0.01"))

    @property
    def discount_amount(self):
        return self.price - self.discounted_price

    def __str__(self) -> str:
        return self.product_name

class ProductImage(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False)
    image = models.ImageField(upload_to='uploads/%y/%m/%d')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
