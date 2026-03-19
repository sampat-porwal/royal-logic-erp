from rest_framework import serializers
from .models import Product, Party, SalesOrder, ProductionJob, DeliveryChallan, PaymentReceipt

# 1. Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'  

# 2. Party Serializer
class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = '__all__'

# 3. 🌟 NAYA: Delivery Challan Serializer
class DeliveryChallanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryChallan
        fields = '__all__'

    # 🌟 NAYA: Data save hone se pehle check karega
    def validate(self, data):
        order = data['order']
        quantity = data['quantity']
        pending_qty = order.ordered_qty - order.delivered_qty
        
        if quantity > pending_qty:
            raise serializers.ValidationError({
                "quantity": f"Error: You can only dispatch up to {pending_qty} meters."
            })
        return data

# 4. 🌟 NAYA: Payment Receipt Serializer
class PaymentReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentReceipt
        fields = '__all__'

    # 🌟 NAYA: Data save hone se pehle check karega
    def validate(self, data):
        order = data['order']
        amount = data['amount']
        balance = order.total_bill - order.amount_received
        
        if amount > balance:
            raise serializers.ValidationError({
                "amount": f"Error: You can only receive up to ₹{balance}."
            })
        return data
# 5. Sales Order Serializer (Updated with History)
class SalesOrderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    # Automatically calculate balance amount
    balance_amount = serializers.SerializerMethodField()
    pending_qty = serializers.SerializerMethodField()
    
    # 🌟 MAGIC: Nested History (Order ke andar uski saari deliveries aur payments bhejega)
    challans = DeliveryChallanSerializer(many=True, read_only=True)
    receipts = PaymentReceiptSerializer(many=True, read_only=True)

    class Meta:
        model = SalesOrder
        fields = [
            'id', 'client', 'client_name', 'product', 'product_name', 
            'ordered_qty', 'delivered_qty', 'pending_qty', 'total_bill', 
            'amount_received', 'balance_amount', 'status', 'created_at',
            'challans', 'receipts' # History fields add kar diye gaye hain
        ]

    def get_balance_amount(self, obj):
        return obj.total_bill - obj.amount_received
        
    def get_pending_qty(self, obj):
        return obj.ordered_qty - obj.delivered_qty 

# core_app/serializers.py ke aakhir mein:

class ProductionJobSerializer(serializers.ModelSerializer):
    # Frontend par dikhane ke liye extra details
    sales_order_display = serializers.CharField(source='sales_order.__str__', read_only=True)
    production_company_name = serializers.CharField(source='production_company.name', read_only=True)
    
    # Automatically calculate Bill and Balance
    total_cost = serializers.SerializerMethodField()
    balance_due = serializers.SerializerMethodField()

    class Meta:
        model = ProductionJob
        fields = [
            'id', 'sales_order', 'sales_order_display', 'production_company', 'production_company_name',
            'given_qty', 'received_qty', 'job_rate_per_meter', 'amount_paid', 
            'total_cost', 'balance_due', 'created_at'
        ]

    def get_total_cost(self, obj):
        return obj.given_qty * obj.job_rate_per_meter

    def get_balance_due(self, obj):
        total = obj.given_qty * obj.job_rate_per_meter
        return total - obj.amount_paid

    # 🌟 ADVANCED ERP LOCKS (Backend Validation)
    def validate(self, data):
        # Yeh tabhi check hoga jab data update ho raha ho (Instance ho)
        if self.instance:
            received = data.get('received_qty', self.instance.received_qty)
            given = data.get('given_qty', self.instance.given_qty)
            paid = data.get('amount_paid', self.instance.amount_paid)
            rate = data.get('job_rate_per_meter', self.instance.job_rate_per_meter)

            # Lock 1: Cannot receive more than given
            if received > given:
                raise serializers.ValidationError({"received_qty": f"Error: Cannot receive more than {given} meters from factory."})

            # Lock 2: Cannot pay more than total cost
            total_bill = given * rate
            if paid > total_bill:
                raise serializers.ValidationError({"amount_paid": f"Error: Cannot pay more than total bill (₹{total_bill})."})

        return data
    

from rest_framework import serializers
from .models import Product, Party, SalesOrder, DeliveryChallan, PaymentReceipt, ProductionJob, JobMaterialReceipt, JobPaymentRecord

# ... (Upar ke purane serializers jaise Product, Party, SalesOrder waise hi rahenge) ...

# 🌟 NAYA: Factory Receipt Serializer (With Lock)
class JobMaterialReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobMaterialReceipt
        fields = '__all__'

    def validate(self, data):
        job = data['job']
        quantity = data['quantity']
        pending = job.given_qty - job.received_qty
        if quantity > pending:
            raise serializers.ValidationError({"quantity": f"Error: Only {pending}m pending from factory."})
        return data

# 🌟 NAYA: Factory Payment Serializer (With Lock)
class JobPaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPaymentRecord
        fields = '__all__'

    def validate(self, data):
        job = data['job']
        amount = data['amount']
        balance = (job.given_qty * job.job_rate_per_meter) - job.amount_paid
        if amount > balance:
            raise serializers.ValidationError({"amount": f"Error: Cannot pay more than balance ₹{balance}."})
        return data

# 🌟 UPDATE: Production Job Serializer (With History)
class ProductionJobSerializer(serializers.ModelSerializer):
    sales_order_display = serializers.CharField(source='sales_order.__str__', read_only=True)
    production_company_name = serializers.CharField(source='production_company.name', read_only=True)
    total_cost = serializers.SerializerMethodField()
    balance_due = serializers.SerializerMethodField()
    
    # Nested History
    material_receipts = JobMaterialReceiptSerializer(many=True, read_only=True)
    payment_records = JobPaymentRecordSerializer(many=True, read_only=True)

    class Meta:
        model = ProductionJob
        fields = [
            'id', 'sales_order', 'sales_order_display', 'production_company', 'production_company_name',
            'given_qty', 'received_qty', 'job_rate_per_meter', 'amount_paid', 
            'total_cost', 'balance_due', 'created_at', 'material_receipts', 'payment_records'
        ]

    def get_total_cost(self, obj):
        return obj.given_qty * obj.job_rate_per_meter

    def get_balance_due(self, obj):
        return (obj.given_qty * obj.job_rate_per_meter) - obj.amount_paid