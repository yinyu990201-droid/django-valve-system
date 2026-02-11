from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ProductListView, ProductDetailView, HomeView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    # API Routes
    path('api/', include(router.urls)),
    
    # Frontend Routes
    path('', HomeView.as_view(), name='home'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<str:pk>/', ProductDetailView.as_view(), name='product-detail'),
]
