from django.urls import path, include
from payments import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/address/', views.address, name='address_create'),
    path('checkout/edit_address/<int:address_id>', views.edit_address, name='edit_address'),
]