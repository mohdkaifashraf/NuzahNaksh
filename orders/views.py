from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Order


@login_required
def order_history(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at", "-id")
    )

    context = {
        'orders':orders
    }

    return render(
        request,
        "orders/order_history.html", context
    )


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items__product"),
        id=order_id,
    )

    payment = order.payments.order_by("-created_at").first()

    context = {
    "order": order,
    "items": order.items.all(),
    "payment": payment,
    "address_lines": (
        order.delivery_address.splitlines()
        if order.delivery_address
        else []
    ),
}

    return render(
        request,
        "orders/order_detail.html",
        context,
    )