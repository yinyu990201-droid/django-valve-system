# Django
from django.shortcuts import render,get_object_or_404
# 项目内
from ..models import CartridgeValve

def product_list(request):
    products = CartridgeValve.objects.all().order_by('-created_at')
    return render(request, 'products/product_list.html', {
        'products': products
    })
def product_detail(request, pk):
    product = get_object_or_404(CartridgeValve, pk=pk)
    return render(request, 'products/product_detail.html', {
        'product': product
    })