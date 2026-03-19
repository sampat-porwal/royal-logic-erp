from django.db import models

# 1. Master Class for Timestamps
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# 2. Product Model
class Product(BaseModel):
    name = models.CharField(max_length=200)
    hsn_code = models.CharField(max_length=20, blank=True)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_meter = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name 

# 3. Party Model (Client & Factory)
class Party(BaseModel):
    PARTY_TYPES = (
        ('CLIENT', 'Client / Buyer'),
        ('PRODUCTION', 'Production / Job Worker'),
    )
    name = models.CharField(max_length=200)
    party_type = models.CharField(max_length=20, choices=PARTY_TYPES)
    phone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.party_type})"

# 4. Sales Order Model
class SalesOrder(BaseModel):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partially Delivered'),
        ('COMPLETED', 'Completed'),
    )
    client = models.ForeignKey(Party, on_delete=models.CASCADE, limit_choices_to={'party_type': 'CLIENT'})
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    ordered_qty = models.DecimalField(max_digits=10, decimal_places=2)
    delivered_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    total_bill = models.DecimalField(max_digits=10, decimal_places=2)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"SO#{self.id} - {self.client.name}"

# 5. Delivery Challan (Order Dispatch History)
class DeliveryChallan(BaseModel):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='challans')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    driver_name = models.CharField(max_length=100, blank=True, null=True)
    vehicle_no = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Challan #{self.id} for SO#{self.order.id} ({self.quantity}m)"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.order.delivered_qty += self.quantity
            if self.order.delivered_qty >= self.order.ordered_qty:
                self.order.status = 'COMPLETED'
            elif self.order.delivered_qty > 0:
                self.order.status = 'PARTIAL'
            self.order.save()
    # (Aapka purana save function yahan hoga...)
    
    # 🌟 NAYA: Delete hone par Minus karega
    def delete(self, *args, **kwargs):
        self.order.delivered_qty -= self.quantity
        
        # Status ko wapas adjust karo
        if self.order.delivered_qty >= self.order.ordered_qty:
            self.order.status = 'COMPLETED'
        elif self.order.delivered_qty > 0:
            self.order.status = 'PARTIAL'
        else:
            self.order.status = 'PENDING'
            
        self.order.save()
        super().delete(*args, **kwargs)

# 6. Payment Receipt (Order Payment History)
class PaymentReceipt(BaseModel):
    PAYMENT_MODES = (('CASH', 'Cash'), ('BANK', 'Bank Transfer/UPI'), ('CHEQUE', 'Cheque'))
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='receipts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES, default='BANK')
    reference_no = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Receipt #{self.id} for SO#{self.order.id} (₹{self.amount})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.order.amount_received += self.amount
            self.order.save()
    
    # 🌟 NAYA: Delete hone par Minus karega
    def delete(self, *args, **kwargs):
        self.order.amount_received -= self.amount
        self.order.save()
        super().delete(*args, **kwargs)

# 7. Production Job Model (Factory Assign)
class ProductionJob(BaseModel):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="production_jobs")
    production_company = models.ForeignKey(Party, on_delete=models.CASCADE, limit_choices_to={'party_type': 'PRODUCTION'})
    
    given_qty = models.DecimalField(max_digits=10, decimal_places=2)
    received_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    job_rate_per_meter = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Job#{self.id} for SO#{self.sales_order.id}"

# -----------------------------------------------------
# 🌟 NAYA: PRODUCTION HISTORY TRACKING 
# -----------------------------------------------------

# 8. Factory se Maal Wapas Aane ka Record
class JobMaterialReceipt(BaseModel):
    job = models.ForeignKey(ProductionJob, on_delete=models.CASCADE, related_name='material_receipts')
    quantity = models.DecimalField(max_digits=10, decimal_places=2) # Kitna bankar aaya
    challan_no = models.CharField(max_length=100, blank=True, null=True) # Factory ka bill number

    def __str__(self):
        return f"Material #{self.id} for JOB#{self.job.id} ({self.quantity}m)"

    # MAGIC: Jab maal aayega, Job mein automatically add ho jayega
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.job.received_qty += self.quantity
            self.job.save()

    # 🌟 NAYA: Delete hone par Minus karega
    def delete(self, *args, **kwargs):
        self.job.received_qty -= self.quantity
        self.job.save()
        super().delete(*args, **kwargs)

# 9. Factory / Karigar ko Payment dene ka Record
class JobPaymentRecord(BaseModel):
    job = models.ForeignKey(ProductionJob, on_delete=models.CASCADE, related_name='payment_records')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50, default='BANK')
    reference_no = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Payment #{self.id} for JOB#{self.job.id} (₹{self.amount})"

    # MAGIC: Jab payment denge, Job mein automatically add ho jayega
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.job.amount_paid += self.amount
            self.job.save()
    
    # 🌟 NAYA: Delete hone par Minus karega
    def delete(self, *args, **kwargs):
        self.job.amount_paid -= self.amount
        self.job.save()
        super().delete(*args, **kwargs)


from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# 1. 📦 SALES DISPATCH: Stock Minus Karo
@receiver(post_save, sender=DeliveryChallan)
def reduce_stock_on_dispatch(sender, instance, created, **kwargs):
    if created:
        product = instance.order.product
        product.stock_quantity -= instance.quantity
        product.save()

@receiver(post_delete, sender=DeliveryChallan)
def restore_stock_on_delete(sender, instance, **kwargs):
    product = instance.order.product
    product.stock_quantity += instance.quantity
    product.save()

# 2. 🏭 PRODUCTION RECEIVE: Stock Plus Karo
@receiver(post_save, sender=JobMaterialReceipt)
def increase_stock_on_receive(sender, instance, created, **kwargs):
    if created:
        # ProductionJob se related sales order ka product dhundo
        product = instance.job.sales_order.product
        product.stock_quantity += instance.quantity
        product.save()

@receiver(post_delete, sender=JobMaterialReceipt)
def decrease_stock_on_delete(sender, instance, **kwargs):
    product = instance.job.sales_order.product
    product.stock_quantity -= instance.quantity
    product.save()