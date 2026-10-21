from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from orders.models import OrderItem, Order
from products.models import Product
from .models import Review
from django.contrib.auth.decorators import login_required

@login_required
def submit_review(request, product_id):
    if request.method != "POST":
        return redirect("product_details", pk=product_id)

    product = get_object_or_404(Product, id=product_id)

    # Check that the customer has received this product.
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        order__status=Order.StatusChoice.DELIVERED,
        product=product
    ).exists()

    if not has_purchased:
        messages.error(
            request,
            "You can review this product only after it has been delivered."
        )
        return redirect("product_details", pk=product.id)

    # Validate the rating.
    try:
        rating = int(request.POST.get("rating", ""))
    except (TypeError, ValueError):
        messages.error(request, "Please select a valid rating.")
        return redirect("product_details", pk=product.id)

    if rating < 1 or rating > 5:
        messages.error(request, "Rating must be between 1 and 5 stars.")
        return redirect("product_details", pk=product.id)

    comment = request.POST.get("comment", "").strip()

    if len(comment) > 500:
        messages.error(request, "Review must be 500 characters or fewer.")
        return redirect("product_details", pk=product.id)

    # Create a review or update the customer's existing review.
    review, created = Review.objects.update_or_create(
        user=request.user,
        product=product,
        defaults={
            "rating": rating,
            "comment": comment,
        }
    )

    if created:
        messages.success(request, "Your review has been submitted.")
    else:
        messages.success(request, "Your review has been updated.")

    return redirect("product_details", pk=product.id)
