from django.contrib import admin
# from django.contrib.auth.models import User
from .models import Address, User

admin.site.register(User)
admin.site.register(Address)
