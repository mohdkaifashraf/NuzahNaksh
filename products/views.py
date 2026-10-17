from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from products.models import Category, Product


def home(request):
    categories = Category.objects.prefetch_related('product_set').all()

    context = {
        'categories':categories
    }

    return render(request, 'products/home.html', context)

def product_detail(request, pk):

    product = get_object_or_404(Product, pk=pk)

    context = {
        'product':product
    }

    return render(request, 'products/product_detail.html', context)