from django.shortcuts import render, redirect, get_object_or_404
from .forms import AddressForm
from django.contrib.auth.decorators import login_required
from carts.models import CartItem, Cart
from decimal import Decimal
from accounts.models import Address


@login_required
def checkout(request):

    addresses = request.user.addresses.all()
    cart = get_object_or_404(Cart, user=request.user)
    
    cart_items = CartItem.objects.filter(cart=cart).select_related("product")

    subtotal = Decimal("0.00")
    for item in cart_items:
        subtotal += item.line_total

    delivery_charge = Decimal("60.00")
    total_amount = subtotal + delivery_charge


    context = {
        'addresses':addresses,
        'cart_items':cart_items,
        'subtotal':subtotal,
        'total_amount':total_amount,
        'delivery_charge':delivery_charge,
    }


    return render(request, 'payments/checkout.html', context)




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