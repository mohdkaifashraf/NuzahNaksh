from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import CASCADE
from django.core.validators import RegexValidator

class User(AbstractUser):
    phone = models.CharField(max_length=50, null= False)

    def __str__(self) -> str:
        return self.first_name

    class Meta:
        db_table ='users'

class Country(models.TextChoices):
    India = 'IN', 'India'
    USA = 'USA', 'United State'





class Address(models.Model):

    ADDRESS_TYPE_CHOICES = [
        ('work', 'Work'),
        ('home', 'Home'),
        ('college', 'College'),
        ('other', 'Other'),
    ]

    User = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='addresses'
    )

    full_name = models.CharField(max_length=50)

    phone_number = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^[6-9][0-9]{9}$',
                message="Enter a valid 10-digit Indian phone number."
            )
        ]
    )

    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)

    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)

    postal_code = models.CharField(max_length=10)

    country = models.CharField(
        max_length=10,
        choices=Country.choices,
        default=Country.India
    )

    address_type = models.CharField(
        max_length=40,
        choices=ADDRESS_TYPE_CHOICES,
        default='home'
    )

    other_address_type = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'addresses'