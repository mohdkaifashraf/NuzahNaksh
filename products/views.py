from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from products.models import Category, Product
from wishlists.models import WishlistItem


def home(request):
    categories = Category.objects.prefetch_related('product_set').all()
    wishlisted_product_ids = set()
    if request.user.is_authenticated:
        wishlisted_product_ids = set(
            WishlistItem.objects.filter(
                wishlist__user=request.user
            ).values_list("product_id", flat=True)
        )

    context = {
        'categories': categories,
        "wishlisted_product_ids": wishlisted_product_ids,
    }

    return render(request, 'products/home.html', context)

def product_detail(request, pk):

    product = get_object_or_404(Product, pk=pk)

    context = {
        'product':product
    }

    return render(request, 'products/product_detail.html', context)