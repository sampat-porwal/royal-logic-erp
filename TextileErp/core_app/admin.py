from django.contrib import admin
from .models import Product, Party, SalesOrder, ProductionJob

# admin.py ke bottom par add karein:
from .models import DeliveryChallan, PaymentReceipt

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'stock_quantity', 'price_per_meter')
    search_fields = ('name',)

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'party_type', 'phone')
    list_filter = ('party_type',)

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    # 'balance_amount' ki jagah 'get_balance_amount' function ko call kiya
    list_display = ('id', 'client', 'product', 'status', 'get_balance_amount')
    list_filter = ('status',)

    # 🌟 NAYA: Admin panel ko bataya ki Balance kaise calculate karna hai
    def get_balance_amount(self, obj):
        return obj.total_bill - obj.amount_received
    
    # Column ka naam set kiya taaki admin mein sundar dikhe
    get_balance_amount.short_description = 'Balance (₹)' 

admin.site.register(ProductionJob)


@admin.register(DeliveryChallan)
class DeliveryChallanAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'quantity', 'created_at')

@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'payment_mode', 'created_at')