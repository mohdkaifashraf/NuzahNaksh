from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import CASCADE

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

    User = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name = 'addresses')
    house_number = models.CharField(max_length=20, blank=True)
    street = models.CharField(max_length=50, blank = False)
    city = models.CharField(max_length=50, blank=False)
    state  = models.CharField(max_length=50, blank= False)
    postal_code = models.IntegerField(blank=False)
    country = models.CharField(max_length=10, choices = Country.choices, default = Country.India,)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'addresses'