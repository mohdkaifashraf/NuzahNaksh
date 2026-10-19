from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse

from products.models import Category, Product
from wishlists.models import Wishlist, WishlistItem


class WishlistTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="wishlist-user",
            password="test-password",
            phone="1234567890",
        )
        category = Category.objects.create(category_name="Handmade")
        self.product = Product.objects.create(
            category=category,
            product_name="Decorative bowl",
            price="100.00",
            stock=2,
        )
        self.client.force_login(self.user)

    def test_toggle_adds_then_removes_product(self):
        url = reverse("toggle_wishlist", args=[self.product.pk])

        add_response = self.client.post(url, {"next": reverse("home")})

        self.assertRedirects(add_response, reverse("home"))
        self.assertTrue(
            WishlistItem.objects.filter(
                wishlist__user=self.user,
                product=self.product,
            ).exists()
        )

        remove_response = self.client.post(url, {"next": reverse("home")})

        self.assertRedirects(remove_response, reverse("home"))
        self.assertFalse(
            WishlistItem.objects.filter(
                wishlist__user=self.user,
                product=self.product,
            ).exists()
        )

    def test_home_marks_saved_products(self):
        wishlist = Wishlist.objects.create(user=self.user)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product)

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.product.pk, response.context["wishlisted_product_ids"])

    def test_wishlist_page_lists_saved_products(self):
        wishlist = Wishlist.objects.create(user=self.user)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product)

        response = self.client.get(reverse("wishlist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.product_name)
