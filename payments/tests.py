from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import override_settings

from carts.models import Cart, CartItem
from orders.models import Order, OrderItem
from payments.models import Payment
from products.models import Category, Product


class AddressEditAuthenticationTests(TestCase):
    def test_edit_address_redirects_anonymous_user_to_login(self):
        response = self.client.get(
            reverse("edit_address", kwargs={"address_id": 1})
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('edit_address', kwargs={'address_id': 1})}",
        )

    def test_authenticated_user_cannot_edit_another_users_address(self):
        from accounts.models import Address

        address_owner = get_user_model().objects.create_user(
            username="address-owner",
            password="test-password",
            phone="1234567890",
        )
        other_user = get_user_model().objects.create_user(
            username="other-user",
            password="test-password",
            phone="1234567891",
        )
        address = Address.objects.create(
            User=address_owner,
            full_name="Address Owner",
            phone_number="9876543210",
            address_line_1="Building 1",
            address_line_2="Main Street",
            city="Lucknow",
            state="Uttar Pradesh",
            postal_code="226001",
            country="IN",
        )
        self.client.force_login(other_user)

        response = self.client.get(
            reverse("edit_address", kwargs={"address_id": address.pk})
        )

        self.assertEqual(response.status_code, 404)


@override_settings(RAZORPAY_KEY_ID="test-key", RAZORPAY_KEY_SECRET="test-secret")
class PaymentInventoryAndInitiationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="payment-user",
            password="test-password",
            phone="1234567890",
        )
        category = Category.objects.create(category_name="Payment category")
        self.product = Product.objects.create(
            category=category,
            product_name="Payment product",
            price=Decimal("100.00"),
            stock=5,
        )
        self.order = Order.objects.create(
            user=self.user,
            delivery_address="Delivery address",
            status=Order.StatusChoice.PENDING,
            subtotal=Decimal("200.00"),
            discount=Decimal("0.00"),
            tax=Decimal("0.00"),
            shipping_charge=Decimal("60.00"),
            total_amount=Decimal("260.00"),
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name=self.product.product_name,
            quantity=2,
            unit_price=Decimal("100.00"),
        )
        self.payment = Payment.objects.create(
            order=self.order,
            amount=self.order.total_amount,
            status=Payment.PaymentStatus.PENDING,
            gateway_order_id="gateway-order-1",
        )
        self.client.force_login(self.user)

    @patch("payments.views.razorpay.Client")
    def test_payment_initiation_reuses_existing_pending_attempt(self, client_class):
        self.payment.delete()
        gateway_client = client_class.return_value
        gateway_client.order.create.return_value = {
            "id": "gateway-order-created",
        }
        initiate_url = reverse(
            "payment_initiate",
            kwargs={"order_id": self.order.pk},
        )

        first_response = self.client.get(initiate_url)
        second_response = self.client.get(initiate_url)

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(
            first_response.context["payment"],
            second_response.context["payment"],
        )
        self.assertEqual(
            second_response.context["razorpay_order_id"],
            "gateway-order-created",
        )
        gateway_client.order.create.assert_called_once()
        self.assertEqual(self.order.payments.count(), 1)

    @patch("payments.views.razorpay.Client")
    def test_successful_payment_decrements_stock_once(self, client_class):
        gateway_client = client_class.return_value
        gateway_client.payment.fetch.return_value = {
            "order_id": self.payment.gateway_order_id,
            "amount": 26000,
            "currency": "INR",
            "status": "captured",
        }
        payload = {
            "order_id": str(self.order.pk),
            "payment_record_id": str(self.payment.pk),
            "razorpay_payment_id": "gateway-payment-1",
            "razorpay_order_id": self.payment.gateway_order_id,
            "razorpay_signature": "valid-signature",
        }

        first_response = self.client.post(reverse("verify_payment"), payload)
        self.product.refresh_from_db()
        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(self.order.items.count(), 1)

        second_response = self.client.post(reverse("verify_payment"), payload)
        self.product.refresh_from_db()
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(self.product.stock, 3)
        gateway_client.payment.fetch.assert_called_once()

    @patch("payments.views.razorpay.Client")
    def test_captured_payment_does_not_confirm_when_stock_is_insufficient(
        self,
        client_class,
    ):
        Product.objects.filter(pk=self.product.pk).update(stock=1)
        client_class.return_value.payment.fetch.return_value = {
            "order_id": self.payment.gateway_order_id,
            "amount": 26000,
            "currency": "INR",
            "status": "captured",
        }
        payload = {
            "order_id": str(self.order.pk),
            "payment_record_id": str(self.payment.pk),
            "razorpay_payment_id": "gateway-payment-1",
            "razorpay_order_id": self.payment.gateway_order_id,
            "razorpay_signature": "valid-signature",
        }

        response = self.client.post(reverse("verify_payment"), payload)

        self.product.refresh_from_db()
        self.payment.refresh_from_db()
        self.assertRedirects(response, reverse("order_history"))
        self.assertEqual(self.product.stock, 1)
        self.assertEqual(self.payment.status, Payment.PaymentStatus.PENDING)
        self.assertEqual(self.order.status, Order.StatusChoice.PENDING)
