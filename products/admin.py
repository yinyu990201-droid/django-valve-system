from django.contrib import admin
from .models import Category, Product, ProductAttachment, PerformanceCurve

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class ProductAttachmentInline(admin.TabularInline):
    model = ProductAttachment
    extra = 1

class PerformanceCurveInline(admin.TabularInline):
    model = PerformanceCurve
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('model_code', 'series', 'category', 'is_active')
    list_filter = ('category', 'series', 'is_active')
    search_fields = ('model_code', 'series')
    inlines = [ProductAttachmentInline, PerformanceCurveInline]

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
