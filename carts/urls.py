from django.urls import path
from carts import views

urlpatterns = [
    path('cart/<int:product_id>/', views.add_item_cart, name='add_item_cart'),
    path('cart/', views.cart, name='cart'),
    path('update/<int:item_id>', views.cart_update, name='cart_update'),
    path('remove/<int:item_id>', views.cart_remove, name='cart_remove'),
]