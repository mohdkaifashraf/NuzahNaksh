from django.urls import path

from . import views

urlpatterns = [
    path("wishlist/", views.wishlist, name="wishlist"),
    path(
        "wishlist/toggle/<int:product_id>/",
        views.toggle_wishlist,
        name="toggle_wishlist",
    ),
]
