from django.contrib import admin
from .models import CartridgeValve,ValveDocument

@admin.register(ValveDocument)
class ValveDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_at")


@admin.register(CartridgeValve)
class CartridgeValveAdmin(admin.ModelAdmin):
    list_display = ('name', 'series')
    filter_horizontal = ("documents",)
from django.contrib import admin

# Register your models here.
