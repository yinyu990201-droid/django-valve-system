from django.views.generic import TemplateView, DetailView
from django_filters.views import FilterView
from .models import CartridgeValve, Category
from .filters import ProductFilter

class HomePageView(TemplateView):
    template_name = 'products/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_categories'] = Category.objects.filter(parent=None)[:6]
        context['recent_products'] = CartridgeValve.objects.order_by('-created_at')[:4]
        return context

class ProductListView(FilterView):
    model = CartridgeValve
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    filterset_class = ProductFilter
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent=None)
        return context

class ProductDetailView(DetailView):
    model = CartridgeValve
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

import os
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from .models import ValveDocument

def download_document(request, doc_id):
    document = get_object_or_404(ValveDocument, id=doc_id)
    file_path = document.file.path
    if not os.path.exists(file_path):
        raise Http404("Document not found")
    
    return FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename=os.path.basename(file_path)
    )
