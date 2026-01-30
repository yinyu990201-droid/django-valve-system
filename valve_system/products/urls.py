from django.urls import path
from .views import file_views,page_views

urlpatterns = [
    path('', page_views.product_list, name='product_list'),
    path('product/<int:pk>/', page_views.product_detail, name='product_detail'),
    path('document/<int:doc_id>/download/', file_views.download_document, name='document_download'),
]
