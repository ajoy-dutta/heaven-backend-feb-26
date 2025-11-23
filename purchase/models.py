from django.db import models
from django.utils import timezone
from person.models import Supplier
from master.models import Company
from product.models import Product
from django.utils.timezone import now
from django.utils.text import slugify




class SupplierPurchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    purchase_date = models.DateField()
    invoice_no = models.CharField(max_length=100, blank=True, null = True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_payable_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    # --- Return summary fields ---
    @property
    def total_returned_quantity(self):
        return sum([p.returned_quantity for p in self.products.all()])

    @property
    def total_returned_value(self):
        return sum([
            p.returned_quantity * p.purchase_price for p in self.products.all()
        ])

    def generate_invoice_no(self):
        last_id = SupplierPurchase.objects.all().order_by('-id').first()
        next_number = (last_id.id + 1) if last_id else 1
        return f"PU{next_number:08d}"

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            self.invoice_no = self.generate_invoice_no()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.invoice_no} - {self.supplier.supplier_name}"




class PurchaseProduct(models.Model):
    purchase = models.ForeignKey(SupplierPurchase, related_name='products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    part_no = models.CharField(max_length=100)
    purchase_quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    purchase_price_with_percentage = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    returned_quantity = models.PositiveIntegerField(default=0)  # New field for tracking returns

    def __str__(self):
        return f"{self.product.part_no} ({self.purchase.invoice_no})"




class PurchasePayment(models.Model):
    purchase = models.ForeignKey(SupplierPurchase, related_name='payments', on_delete=models.CASCADE)
    payment_mode = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    account_no = models.CharField(max_length=100, blank=True, null=True)
    cheque_no = models.CharField(max_length=100, blank=True, null=True)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Payment for {self.purchase.invoice_no}"
    




class SupplierPurchaseReturn(models.Model):
    purchase_product = models.ForeignKey(PurchaseProduct, related_name='returns', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    return_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return {self.quantity} of {self.purchase_product} on {self.return_date}" 



class Order(models.Model):
    order_no = models.CharField(max_length=30, unique=True, blank=True)
    order_date = models.DateField(default=now)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='orders',blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.order_no:
            today = now().strftime('%Y%m%d')
            last_order = Order.objects.filter(order_no__startswith=f"ORD-{today}").order_by('id').last()
            next_number = 1

            if last_order:
                try:
                    last_no = last_order.order_no.split('-')[-1]
                    next_number = int(last_no) + 1
                except:
                    pass

            self.order_no = f"ORD-{today}-{next_number:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_no



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    order_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.product_name if self.product else 'No Product'} ({self.quantity})"





class Purchase(models.Model):
    invoice_no = models.CharField(max_length=100)
    purchase_date = models.DateField()
    exporter_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.invoice_no} ({self.purchase_date})"



class PurchaseItem(models.Model):
    purchase = models.ForeignKey(
        Purchase,
        related_name="items",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE,blank=True, null=True)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product} - Qty {self.quantity}"