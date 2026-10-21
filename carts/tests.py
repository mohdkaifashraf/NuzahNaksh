from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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

    def test_cart_page_shows_empty_state_when_user_has_no_cart(self):
        user = get_user_model().objects.create_user(
            username="empty-cart-user",
            password="test-password",
            phone="1234567890",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("cart"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your cart is waiting")
        self.assertFalse(Cart.objects.filter(user=user).exists())

    def test_add_to_cart_rejects_invalid_quantity_without_server_error(self):
        product = Product.objects.create(
            category=self.cart.cartitem_set.first().product.category,
            product_name="Quantity test product",
            price=Decimal("25.00"),
            stock=5,
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("add_item_cart", kwargs={"product_id": product.pk}),
            {"quantity": "not-a-number"},
        )

        self.assertRedirects(
            response,
            reverse("product_details", kwargs={"pk": product.pk}),
        )
        self.assertFalse(
            CartItem.objects.filter(cart=self.cart, product=product).exists()
        )

    def test_add_to_cart_rejects_get_requests(self):
        product = self.cart.cartitem_set.first().product
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("add_item_cart", kwargs={"product_id": product.pk}),
        )

        self.assertEqual(response.status_code, 405)

    def test_cart_update_rejects_quantity_above_stock(self):
        product = Product.objects.create(
            category=self.cart.cartitem_set.first().product.category,
            product_name="Stock limited product",
            price=Decimal("25.00"),
            stock=4,
        )
        item = CartItem.objects.create(
            cart=self.cart,
            product=product,
            quantity=2,
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("cart_update", kwargs={"item_id": item.pk}),
            {"quantity": "5"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)
        self.assertContains(response, "Only 4 units are available.")

    def test_cart_quantity_input_uses_product_stock_as_maximum(self):
        product = Product.objects.create(
            category=self.cart.cartitem_set.first().product.category,
            product_name="Stock maximum product",
            price=Decimal("25.00"),
            stock=4,
        )
        CartItem.objects.create(cart=self.cart, product=product, quantity=2)
        self.client.force_login(self.user)

        response = self.client.get(reverse("cart"))

        self.assertContains(response, f'max="4"', html=False)
        self.assertContains(response, "js/cart.js")

    def test_product_detail_button_shows_added_state_after_add_to_cart(self):
        product = Product.objects.create(
            category=self.cart.cartitem_set.first().product.category,
            product_name="Added state product",
            price=Decimal("25.00"),
            stock=5,
        )
        self.client.force_login(self.user)

        initial_response = self.client.get(
            reverse("product_details", kwargs={"pk": product.pk})
        )
        self.assertContains(initial_response, "Add to Cart")
        self.assertNotContains(initial_response, "Added to Cart")

        add_response = self.client.post(
            reverse("add_item_cart", kwargs={"product_id": product.pk}),
            {"quantity": "1"},
        )
        self.assertRedirects(
            add_response,
            reverse("product_details", kwargs={"pk": product.pk}),
        )

        detail_response = self.client.get(
            reverse("product_details", kwargs={"pk": product.pk})
        )
        self.assertContains(detail_response, "Added to Cart")
        self.assertEqual(
            CartItem.objects.get(cart=self.cart, product=product).quantity,
            1,
        )
