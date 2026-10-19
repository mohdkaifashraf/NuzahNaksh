from django.urls import path, include
from products import views

urlpatterns = [
    path('products/<int:pk>/', views.product_detail, name='product_details'),
    path('', include('carts.urls'))
]