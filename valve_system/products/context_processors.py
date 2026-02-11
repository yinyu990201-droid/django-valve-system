from .models import Category

def categories_processor(request):
    # Fetch root categories (those without a parent) using 'prefetch_related' 
    # for efficiency if we were doing deep nesting, but for simple recursion
    # in templates, getting roots is the starting point.
    # Note: For deep trees, MPTT is better, but for this scale, recursive logic is fine.
    root_categories = Category.objects.filter(parent=None).prefetch_related('children')
    return {'root_categories': root_categories}
