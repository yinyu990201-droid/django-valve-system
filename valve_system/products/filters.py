import django_filters
from django.db.models import Q
from .models import CartridgeValve, Category

class ProductFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Search')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all(), label='Category')
    max_pressure_min = django_filters.NumberFilter(field_name='max_pressure', lookup_expr='gte', label='Min Pressure')
    max_flow_min = django_filters.NumberFilter(field_name='max_flow', lookup_expr='gte', label='Min Flow')

    class Meta:
        model = CartridgeValve
        fields = ['category', 'series', 'material']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | 
            Q(series__icontains=value) | 
            Q(description__icontains=value) |
            Q(application__icontains=value)
        )
