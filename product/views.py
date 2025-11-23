from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from rest_framework.decorators import action


# ----------------------------
# Category
# ----------------------------
class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.select_related('company').all()
    serializer_class = ProductCategorySerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['category_name', 'company__company_name']
    filterset_fields = ['company']


# ----------------------------
# Bike Model  ✅ NEW
# ----------------------------
class BikeModelViewSet(viewsets.ModelViewSet):
    """
    Supports:
      - GET /bike-models/?company=<id>
      - GET /bike-models/?search=glam
      - POST multipart (company, name, image)
    """
    queryset = BikeModel.objects.select_related('company').all()
    serializer_class = BikeModelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'company__company_name']
    filterset_fields = ['company']


# ----------------------------
# Product
# ----------------------------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category', 'bike_model').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]

    search_fields = [
        'product_name',
        'part_no',
        'brand_name',
        'model_no',
    ]

    filterset_fields = ['company', 'category', 'bike_model', 'model_no']

    def get_queryset(self):
        qs = super().get_queryset()

        # Filter by company (CharField)
        company = self.request.query_params.get('company')
        if company:
            qs = qs.filter(company=company)

        # Filter by bike_model (FK)
        bike_model = self.request.query_params.get('bike_model')
        if bike_model:
            qs = qs.filter(bike_model_id=bike_model)

        # Filter by model no
        model_no = self.request.query_params.get('model_no')
        if model_no:
            qs = qs.filter(model_no__iexact=model_no)

        # Filter by brand name
        brand_name = self.request.query_params.get('brand_name')
        if brand_name:
            qs = qs.filter(brand_name__iexact=brand_name)

        return qs



# ----------------------------
# Stock
# ----------------------------
class StockViewSet(viewsets.ModelViewSet):
    queryset = StockProduct.objects.all()
    serializer_class = StockSerializer

    @action(detail=True, methods=['patch'], url_path="set-damage-quantity")
    def set_damage_quantity(self, request, pk=None):
        stock = self.get_object()
        damage_qty = request.data.get("damage_quantity")

        # Validate
        try:
            damage_qty = int(damage_qty)
        except:
            return Response(
                {"error": "damage_quantity must be a number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if damage_qty < 0:
            return Response(
                {"error": "damage_quantity cannot be negative"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the stock damage quantity
        stock.current_stock_quantity = max(stock.current_stock_quantity - damage_qty, 0)
        stock.damage_quantity += damage_qty
        stock.save()

        return Response(
            {"message": "Damage quantity updated successfully", "data": StockSerializer(stock).data},
            status=status.HTTP_200_OK
        )

