from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class ProductSearchTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(category_name="Handmade art")
        self.product = Product.objects.create(
            category=self.category,
            product_name="Silver pendant",
            product_description="A floral handmade keepsake",
            price="125.00",
            stock=0,
        )

    def test_search_matches_product_description_and_includes_out_of_stock(self):
        response = self.client.get(reverse("home"), {"q": "FLORAL"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.product_name)
        self.assertContains(response, "Out of stock")

    def test_search_matches_category_name(self):
        response = self.client.get(reverse("home"), {"q": "handmade art"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.product_name)

    def test_search_shows_empty_state_when_no_products_match(self):
        response = self.client.get(reverse("home"), {"q": "not found"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No products matched")
        self.assertNotContains(response, self.product.product_name)

    def test_product_detail_displays_related_products_from_same_category(self):
        related = Product.objects.create(
            category=self.category,
            product_name="Matching category item",
            product_description="Related product",
            price="75.00",
            stock=2,
        )
        other_category = Category.objects.create(category_name="Other")
        Product.objects.create(
            category=other_category,
            product_name="Unrelated category item",
            product_description="Not related",
            price="50.00",
            stock=2,
        )

        response = self.client.get(
            reverse("product_details", kwargs={"pk": self.product.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["related_products"]),
            [related],
        )
        self.assertContains(
            response,
            reverse("product_details", kwargs={"pk": related.pk}),
        )
