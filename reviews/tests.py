from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from products.models import Category, Product
from .models import Review


class ReviewTimestampTests(TestCase):
    def test_editing_review_preserves_original_creation_timestamp(self):
        user = get_user_model().objects.create_user(
            username="reviewer",
            password="test-password",
            phone="1234567890",
        )
        category = Category.objects.create(category_name="Review category")
        product = Product.objects.create(
            category=category,
            product_name="Review product",
            price="10.00",
        )
        review = Review.objects.create(
            user=user,
            product=product,
            rating=4,
            comment="Original comment",
        )
        original_created_at = timezone.now() - timedelta(days=1)
        Review.objects.filter(pk=review.pk).update(
            created_at=original_created_at
        )

        Review.objects.update_or_create(
            user=user,
            product=product,
            defaults={"rating": 5, "comment": "Updated comment"},
        )
        review.refresh_from_db()

        self.assertEqual(review.created_at, original_created_at)
        self.assertEqual(review.comment, "Updated comment")
        self.assertGreater(review.updated_at, original_created_at)
