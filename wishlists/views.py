from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from products.models import Product
from .models import Wishlist, WishlistItem


@login_required
def wishlist(request):
    wishlist_items = WishlistItem.objects.filter(
        wishlist__user=request.user
    ).select_related("product")

    context = {
        "wishlist_items": wishlist_items
    }
    return render(
        request,
        "wishlists/wishlist.html",
        context
    )


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist_item = WishlistItem.objects.filter(
        wishlist=wishlist,
        product=product,
    )

    if wishlist_item.exists():
        wishlist_item.delete()
        messages.success(request, f"{product.product_name} removed from your wishlist.")
    else:
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        messages.success(request, f"{product.product_name} added to your wishlist.")

    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse("home")
    return redirect(next_url)
