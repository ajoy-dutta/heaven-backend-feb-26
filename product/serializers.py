from .models import *
from rest_framework import serializers
from master.serializers import CompanySerializer
from person.models import Supplier
from person.serializers import SupplierSerializer


# ----------------------------
# Category Serializer
# ----------------------------
class ProductCategorySerializer(serializers.ModelSerializer):
    company_detail = CompanySerializer(source='company', read_only=True)

    class Meta:
        model = ProductCategory
        fields = ['id', 'company', 'company_detail', 'category_name']


# ----------------------------
# Bike Model Serializer
# ----------------------------
class BikeModelSerializer(serializers.ModelSerializer):
    company_detail = CompanySerializer(source="company", read_only=True)

    class Meta:
        model = BikeModel
        fields = ["id", "company", "company_detail", "name", "image", "slug"]


# ----------------------------
# Product Serializer
# ----------------------------
class ProductSerializer(serializers.ModelSerializer):
    category_detail = ProductCategorySerializer(source='category', read_only=True)
    bike_model_detail = BikeModelSerializer(source="bike_model", read_only=True)

    class Meta:
        model = Product
        fields = '__all__'



# ----------------------------
# Stock Serializer
# ----------------------------
class StockSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = StockProduct
        fields = '__all__'

