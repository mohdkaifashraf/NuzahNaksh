from django.urls import path, include
from payments import views

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/address/", views.address, name="address_create"),
    path(
        "checkout/edit_address/<int:address_id>/",
        views.edit_address,
        name="edit_address",
    ),
    path(
        "initiate/<int:order_id>/", views.payment_initiate, name="payment_initiate"),
        path("verify/", views.verify_payment, name="verify_payment",),
]