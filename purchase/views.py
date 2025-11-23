from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.views import APIView
from decimal import Decimal
from product.models import Product, StockProduct
import pandas as pd
from django.db import transaction


# ----------------------------
# Supplier Purchase
# ----------------------------
class SupplierPurchaseViewSet(viewsets.ModelViewSet):
    queryset = SupplierPurchase.objects.all().order_by('-purchase_date')
    serializer_class = SupplierPurchaseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]



# ----------------------------
# Supplier Purchase Return
# ----------------------------
class SupplierPurchaseReturnViewSet(viewsets.ModelViewSet):
    queryset = SupplierPurchaseReturn.objects.all().order_by('-return_date')
    serializer_class = SupplierPurchaseReturnSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        invoice_no = self.request.query_params.get('invoice_no')
        if invoice_no:
            queryset = queryset.filter(purchase_product__purchase__invoice_no=invoice_no)
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save()
        purchase_product = instance.purchase_product
        # Update returned_quantity
        purchase_product.returned_quantity += instance.quantity
        purchase_product.save()
        # Update stock
        stock = StockProduct.objects.filter(
            company_name=purchase_product.purchase.company_name,
            part_no=purchase_product.part_no,
            product=purchase_product.product
        ).first()
        if stock:
            stock.current_stock_quantity = max(stock.current_stock_quantity - instance.quantity, 0)
            stock.save()


# ----------------------------
# Order
# ----------------------------
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]




def create_purchase_entry(data):
    try:
        company = Company.objects.get(id=data["company_id"])
    except Company.DoesNotExist:
        raise ValueError("Company not found")
    

    try:
        product = Product.objects.get(part_no=data["part_no"])
    except Product.DoesNotExist:
        raise ValueError("Product not found")

    # Get or create the Purchase
    purchase, created = Purchase.objects.get_or_create(
        invoice_no=data["invoice_no"],
        purchase_date =data["purchase_date"],
        defaults={
            "exporter_name": data["exporter_name"],
            "company_name": company.company_name,
        }
    )

    # Create PurchaseItem
    purchase_item = PurchaseItem.objects.create(
        purchase=purchase,
        product=product,
        quantity=data["quantity"],
        purchase_price=data["purchase_price"],
        total_price= Decimal(data["quantity"]) * Decimal(data["purchase_price"]),
    )

    return purchase_item




def update_stock(product, company_name, quantity, price, unit):
    
    stock, created = StockProduct.objects.get_or_create(
        product=product,
        part_no=product.part_no,
        defaults={
            "company_name": company_name,
            "purchase_quantity": quantity,
            "sale_quantity": 0,
            "damage_quantity": 0,
            "current_stock_quantity": quantity,
            "purchase_price": price,
            "sale_price": price,
            "current_stock_value": quantity * price,
        }
    )

    
    if not created:
        stock.purchase_quantity += quantity
        stock.current_stock_quantity += quantity
        stock.purchase_price = price
        stock.current_stock_value += Decimal(quantity) * Decimal(price)
        stock.save()

    return stock



class UploadStockExcelView(APIView):
    def post(self, request):
        file = request.FILES.get("xl_file")
        company_id = request.data.get("company_name")
        exporter_name = request.data.get("exporter_name")
        invoice_no = request.data.get("invoice_no", "AUTO_GENERATE")
        purchase_date = request.data.get("purchase_date")

        # Validate company
        # try:
        #     company = Company.objects.get(id=company_id)
        # except Company.DoesNotExist:
        #     return Response({"error": "No Company Selected or Found"}, status=400)

        # Validate file
        if not file:
            return Response({"error": "No file uploaded"}, status=400)
        if not file.name.endswith(".xlsx"):
            return Response({"error": "Please upload an .xlsx file"}, status=400)

        # Read Excel
        try:
            df = pd.read_excel(file, engine="openpyxl")
        except Exception as e:
            return Response({"error": f"Invalid Excel file: {str(e)}"}, status=400)

        
        created_stocks = []
        with transaction.atomic():
            for _, row in df.iterrows():
                product_name = str(row["Description"]).strip()
                part_no = str(row["Part_no"]).strip()
                company_name = str(row["Group"]).strip()
                price = float(row["Rate"])
                quantity = int(row["Qty"])
                unit = str(row["Unit"])

                print("Processing:", part_no, price, quantity, unit, company_name)

                product, created = Product.objects.get_or_create(
                    part_no=part_no,
                    defaults={
                        "company": company_name,
                        "category": None, 
                        "product_name": product_name,
                        "product_mrp": price,
                        'unit' : unit,
                    }
                )

                # Update product MRP
                if not created:
                    product.product_mrp = price
                    product.save()

                # Update stock using the helper function
                update_stock(product, company_name, quantity, price, unit)

                # Create purchase entry
                create_purchase_entry({
                    "invoice_no": invoice_no,
                    "purchase_date": purchase_date,
                    "exporter_name": exporter_name,
                    "company_id": company_id,
                    "part_no": part_no,
                    "quantity": quantity,
                    "purchase_price": price,
                })

                created_stocks.append({
                    "product": product.product_name,
                    "part_no": product.part_no,
                    "added_quantity": quantity,
                    "updated_mrp": price,
                })

        return Response({
            "message": "Stock uploaded successfully",
            "items": created_stocks
        }, status=200)
