from rest_framework import serializers
from .models import Category, Product, ProductAttachment, PerformanceCurve

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductAttachmentSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_file_type_display', read_only=True)

    class Meta:
        model = ProductAttachment
        fields = ['id', 'file', 'file_type', 'type_display', 'title']

class PerformanceCurveSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceCurve
        fields = ['id', 'curve_type', 'data_points']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    attachments = ProductAttachmentSerializer(many=True, read_only=True)
    performance_curves = PerformanceCurveSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
