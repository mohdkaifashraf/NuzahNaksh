from django.shortcuts import render, redirect, get_object_or_404
from .forms import AddressForm
from django.contrib.auth.decorators import login_required
from carts.models import CartItem, Cart
from decimal import Decimal
from accounts.models import Address
from django.contrib import messages
from django.db import transaction
from orders.models import Order, OrderItem
from django.conf import settings
import razorpay
from .models import Payment


@login_required
def checkout(request):
    addresses = request.user.addresses.all()

    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(
        cart=cart
    ).select_related("product")

    selected_address_id = request.POST.get("address_id", "")

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("cart_detail")

    subtotal = sum(
        (item.line_total for item in cart_items),
        Decimal("0.00")
    )

    delivery_charge = Decimal("60.00")
    total_amount = subtotal + delivery_charge

    if request.method == "POST":
        address_id = request.POST.get("address_id")

        if not address_id:
            messages.error(request, "Please select a delivery address.")
        else:
            selected_address = get_object_or_404(
                Address,
                id=address_id,
                User=request.user
            )

            # Recalculate totals and create the order atomically.
            with transaction.atomic():
                cart_items = list(
                    CartItem.objects.filter(cart=cart)
                    .select_related("product")
                    .select_for_update()
                )

                if not cart_items:
                    messages.error(request, "Your cart is empty.")
                    return redirect("cart_detail")

                # Recalculate using the current database prices.
                subtotal = sum(
                    (item.line_total for item in cart_items),
                    Decimal("0.00")
                )

                # Validate stock before creating the order.
                for item in cart_items:
                    if item.quantity < 1:
                        messages.error(
                            request,
                            "Invalid product quantity in your cart."
                        )
                        return redirect("checkout")

                    if item.quantity > item.product.stock:
                        messages.error(
                            request,
                            f"Insufficient stock for {item.product.product_name}."
                        )
                        return redirect("checkout")

                total_amount = subtotal + delivery_charge

                address_snapshot = (
                    f"{selected_address.full_name}\n"
                    f"{selected_address.phone_number}\n"
                    f"{selected_address.address_line_1}\n"
                    f"{selected_address.address_line_2}\n"
                    f"{selected_address.city}, "
                    f"{selected_address.state} "
                    f"{selected_address.postal_code}\n"
                    f"{selected_address.country}"
                )

                order = Order.objects.create(
                    user=request.user,
                    delivery_address=address_snapshot,
                    status=Order.StatusChoice.PENDING,
                    subtotal=subtotal,
                    discount=Decimal("0.00"),
                    tax=Decimal("0.00"),
                    shipping_charge=delivery_charge,
                    total_amount=total_amount,
                )

                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.product_name,
                        quantity=item.quantity,
                        unit_price=item.product.discounted_price,
                        discount=Decimal("0.00"),
                    )

            # Next step: initiate payment for this pending order.
            return redirect("payment_initiate", order_id=order.id)

    context = {
        "addresses": addresses,
        "cart_items": cart_items,
        "subtotal": subtotal,
        "total_amount": total_amount,
        "delivery_charge": delivery_charge,
        "selected_address_id": selected_address_id,
    }

    return render(request, "payments/checkout.html", context)




@login_required
def address(request):

    if request.method == 'POST':
        form = AddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)

            address.User = request.user

            address.save()

            return redirect('checkout')

    else:
        form = AddressForm

    context = {
        'form':form
    }

    return render(request, 'payments/address.html', context)



def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, User=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)

        if form.is_valid():
            form.save()
            return redirect('checkout')
    else:
        form = AddressForm(instance=address)

    context = {
        'form':form,
        'address':address
    }

    return render(request, 'payments/address.html', context )



@login_required
def payment_initiate(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status=Order.StatusChoice.PENDING,
    )

    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        messages.error(request, "Payment gateway is not configured.")
        return redirect("checkout")

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )
    )

    try:
        # Razorpay expects the amount in paise.
        amount_paise = int(order.total_amount * Decimal("100"))

        razorpay_order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"order_{order.id}",
        })

        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            payment_method=Payment.PaymentMethod.RAZORPAY,
            status=Payment.PaymentStatus.PENDING,
            gateway_order_id=razorpay_order["id"],
        )

    except Exception:
        messages.error(
            request,
            "Unable to start payment right now. Please try again."
        )
        return redirect("checkout")

    context = {
        "order": order,
        "payment": payment,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"],
        "amount_paise": amount_paise,
    }

    return render(request, "payments/payment.html", context)




@login_required
def verify_payment(request):
    if request.method != "POST":
        return redirect("checkout")

    order_id = request.POST.get("order_id")
    payment_record_id = request.POST.get("payment_record_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    # Make sure all required values were submitted.
    if not all([
        order_id,
        payment_record_id,
        razorpay_payment_id,
        razorpay_order_id,
        razorpay_signature,
    ]):
        messages.error(request, "Payment verification details are missing.")
        return redirect("checkout")

    # Only access orders belonging to the logged-in customer.
    order = get_object_or_404(
        Order,
        pk=order_id,
        user=request.user,
    )

    payment = get_object_or_404(
        Payment,
        pk=payment_record_id,
        order=order,
    )

    # Handle repeated submissions safely.
    if payment.status == Payment.PaymentStatus.SUCCESS:
        return render(
            request,
            "payments/payment_result.html",
            {"order": order, "success": True},
        )

    # Check that the submitted Razorpay order matches our database.
    if payment.gateway_order_id != razorpay_order_id:
        messages.error(request, "The payment order does not match.")
        return redirect("checkout")

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )
    )

    try:
        # Verify the signature using the server-side secret.
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        })

        # Retrieve payment details directly from Razorpay.
        gateway_payment = client.payment.fetch(razorpay_payment_id)

        expected_amount = int(order.total_amount * Decimal("100"))

        # Validate the gateway payment against our order.
        if (
            gateway_payment.get("order_id") != payment.gateway_order_id
            or gateway_payment.get("amount") != expected_amount
            or gateway_payment.get("currency") != "INR"
        ):
            messages.error(request, "Payment details could not be verified.")
            return redirect("checkout")

        # Signature verification is not, by itself, proof that funds
        # have been captured. Only finalize when Razorpay says captured.
        if gateway_payment.get("status") != "captured":
            messages.warning(
                request,
                "Your payment has not been captured yet. Please check its status.",
            )
            return redirect("checkout")

    except razorpay.errors.SignatureVerificationError:
        messages.error(request, "Payment signature verification failed.")
        return redirect("checkout")

    except Exception:
        messages.error(
            request,
            "We couldn't verify your payment right now. Please try again.",
        )
        return redirect("checkout")

    # Update records together so a partial database update isn't committed.
    with transaction.atomic():
        order = Order.objects.select_for_update().get(
            pk=order.pk,
            user=request.user,
        )
        payment = Payment.objects.select_for_update().get(
            pk=payment.pk,
            order=order,
        )

        # Recheck after acquiring locks to handle duplicate submissions.
        if payment.status != Payment.PaymentStatus.SUCCESS:
            payment.transaction_id = razorpay_payment_id
            payment.status = Payment.PaymentStatus.SUCCESS
            payment.save(update_fields=[
                "transaction_id",
                "status",
                "updated_at",
            ])

            order.status = Order.StatusChoice.CONFIRMED
            order.save(update_fields=["status", "updated_at"])

            # Clear the cart only after verified payment.

            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                CartItem.objects.filter(cart=cart).delete()

    return render(
        request,
        "payments/payment_result.html",
        {"order": order, "success": True},
    )
