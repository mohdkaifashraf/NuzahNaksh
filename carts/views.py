from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from django.contrib import messages
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required 
from decimal import Decimal
from django.views.decorators.http import require_POST


@login_required
def add_item_cart(request, product_id):

    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get("quantity", 1))

    if quantity < 1 or quantity > product.stock:
        messages.error(request, "Invalid quantity or insufficient stock.")
        return redirect("product_details", pk=product.pk)

    cart, created = Cart.objects.get_or_create(user = request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity},
    )

    if not created:
        new_quantity = item.quantity + quantity

        if new_quantity > product.stock:
            messages.error(request, "Not enough stock available.")
            return redirect("product_details", pk=product.pk)

        item.quantity = new_quantity
        item.save(update_fields=["quantity"])

    messages.success(request, "Product added to your cart.")

    return redirect('product_details', pk=product.id)


@login_required
def cart(request):

    cart = get_object_or_404(Cart, user=request.user)

    cart_items = CartItem.objects.filter(cart=cart).select_related("product")

    subtotal = Decimal("0.00")
    for item in cart_items:
        subtotal += item.line_total

    delivery_charge = Decimal("60.00")
    total_amount = subtotal + delivery_charge

    context = {
        "cart": cart,
        "cart_items": cart_items,
        "total_amount": total_amount,
        "subtotal": subtotal,
        "delivery_charge": delivery_charge,
    }

    return render(request, 'carts/cart.html', context)

@login_required
@require_POST
def cart_update(request, item_id):

    item = get_object_or_404(CartItem, pk=item_id, cart__user = request.user)

    try:
        quantity = int(request.POST.get("quantity", ""))

    except (TypeError, ValueError):
        messages.error(request, "Please enter a valid quantity.")
        return redirect("cart")

    if quantity < 1:
        messages.error(request, "Quantity must be at least 1.")
        return redirect("cart")

    if quantity > item.product.stock:
        messages.error(request, f"Only {item.product.stock} units are available.")
        return redirect("cart")

    item.quantity = quantity
    item.save(update_fields=['quantity'])
    messages.success(request, "Cart quantity updated successfully.")
    return redirect("cart")


@login_required
@require_POST
def cart_remove(request, item_id):

    item = get_object_or_404(CartItem, pk=item_id, cart__user = request.user)

    item.delete()

    messages.success(request, "Item removed from your cart.")
    return redirect("cart")


