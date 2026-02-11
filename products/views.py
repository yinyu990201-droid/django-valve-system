from rest_framework import viewsets, filters, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

# --- API ViewSets ---

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'series', 'cavity', 'material', 'is_active']
    search_fields = ['model_code', 'description', 'series']
    ordering_fields = ['model_code', 'created_at']
    ordering = ['model_code']

    @action(detail=False, methods=['get'])
    def search_autocomplete(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])
        
        products = Product.objects.filter(model_code__icontains=query)[:10]
        results = [{'value': p.model_code, 'label': f"{p.model_code} - {p.series}"} for p in products]
        return Response(results)

# --- Frontend Views ---

class HomeView(TemplateView):
    template_name = 'home.html'

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Filtering
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
            
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(model_code__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(series__icontains=search_query)
            )
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent=None).prefetch_related('children')
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context

    def render_to_response(self, context, **response_kwargs):
        # HTMX support: render only the grid if the request is from HTMX
        if self.request.headers.get('HX-Request'):
            return self.response_class(
                request=self.request,
                template=['products/components/product_grid.html'],
                context=context,
                using=self.template_engine,
                **response_kwargs
            )
        return super().render_to_response(context, **response_kwargs)

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['performance_curves'] = self.object.performance_curves.all()
        return context
