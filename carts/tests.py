from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from carts.models import Cart, CartItem
from products.models import Category, Product


class CartTotalsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cart-user",
            password="test-password",
            phone="1234567890",
        )
        self.cart = Cart.objects.create(user=self.user)
        category = Category.objects.create(category_name="Handmade")
        first_product = Product.objects.create(
            category=category,
            product_name="Decorative bowl",
            price=Decimal("100.00"),
            discount_percentage=10,
        )
        second_product = Product.objects.create(
            category=category,
            product_name="Small vase",
            price=Decimal("50.00"),
            discount_percentage=20,
        )
        CartItem.objects.create(cart=self.cart, product=first_product, quantity=2)
        CartItem.objects.create(cart=self.cart, product=second_product, quantity=3)

    def test_cart_totals_use_discounted_prices_for_every_item(self):
        self.client.force_login(self.user)

        response = self.client.get("/cart/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["subtotal"], Decimal("300.00"))
        self.assertEqual(response.context["delivery_charge"], Decimal("60.00"))
        self.assertEqual(response.context["total_amount"], Decimal("360.00"))
        self.assertEqual(
            [item.line_total for item in response.context["cart_items"]],
            [Decimal("180.00"), Decimal("120.00")],
        )
