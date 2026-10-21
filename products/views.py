from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count, Prefetch, Q
from products.models import Category, Product
from wishlists.models import WishlistItem
from orders.models import OrderItem, Order
from reviews.models import Review
from carts.models import CartItem

def home(request):
    search_query = request.GET.get("q", "").strip()
    products = Product.objects.order_by("pk")

    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query)
            | Q(product_description__icontains=search_query)
            | Q(category__category_name__icontains=search_query)
        )
        categories = Category.objects.filter(
            product__in=products
        ).distinct()
    else:
        products = products.filter(stock__gt=0)
        categories = Category.objects.all()

    categories = categories.prefetch_related(
        Prefetch(
            "product_set",
            queryset=products,
            to_attr="display_products",
        )
    )

    wishlisted_product_ids = set()
    if request.user.is_authenticated:
        wishlisted_product_ids = set(
            WishlistItem.objects.filter(
                wishlist__user=request.user
            ).values_list("product_id", flat=True)
        )

    context = {
        "categories": categories,
        "search_query": search_query,
        "wishlisted_product_ids": wishlisted_product_ids,
    }

    return render(request, 'products/home.html', context)

def product_detail(request, pk):

    product = get_object_or_404(Product, pk=pk)
    reviews = (
        Review.objects
        .filter(product=product)
        .select_related("user")
        .order_by("-created_at", "-id")
    )
    review_summary = reviews.aggregate(
        average_rating=Avg("rating"),
        review_count=Count("id"),
    )
    can_review = False
    existing_review = None
    product_in_cart = False

    if request.user.is_authenticated:
        product_in_cart = CartItem.objects.filter(
            cart__user=request.user,
            product=product,
        ).exists()

        can_review = OrderItem.objects.filter(
            order__user=request.user,
            order__status=Order.StatusChoice.DELIVERED,
            product=product
        ).exists()

        existing_review = Review.objects.filter(
            user=request.user,
            product=product
        ).first()

    context = {
        "product": product,
        "reviews": reviews,
        "average_rating": review_summary["average_rating"],
        "review_count": review_summary["review_count"],
        "can_review": can_review,
        "existing_review": existing_review,
        "user_has_reviewed": existing_review is not None,
        "product_in_cart": product_in_cart,
        "related_products": (
            Product.objects
            .filter(category=product.category, stock__gt=0)
            .exclude(pk=product.pk)
            .order_by("pk")[:4]
        ),
    }

    return render(request, 'products/product_detail.html', context)