from django.shortcuts import render
from .models import Product

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Product
from .serializers import ProductSerializer

from .models import Party, SalesOrder
from .serializers import PartySerializer, SalesOrderSerializer


from .models import DeliveryChallan, PaymentReceipt
from .serializers import DeliveryChallanSerializer, PaymentReceiptSerializer


from .models import ProductionJob
from .serializers import ProductionJobSerializer

from .models import JobMaterialReceipt, JobPaymentRecord
from .serializers import JobMaterialReceiptSerializer, JobPaymentRecordSerializer

def product_list(request):
    # Fetch all products from the database
    products = Product.objects.all()
    return render(request, 'core_app/product_list.html', {'products': products})



# Yeh class GET aur POST dono handle karegi automatically!
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('-id') # Latest pehle dikhega
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated] # Sirf login wale Next.js users access kar payenge



# Views.py mein sabse neeche add karein:
class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]



class PartyListCreateView(generics.ListCreateAPIView):
    queryset = Party.objects.all()
    serializer_class = PartySerializer
    permission_classes = [IsAuthenticated]

class SalesOrderListCreateView(generics.ListCreateAPIView):
    queryset = SalesOrder.objects.all().order_by('-created_at')
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated]


class SalesOrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated]



class DeliveryChallanListCreateView(generics.ListCreateAPIView):
    queryset = DeliveryChallan.objects.all().order_by('-created_at')
    serializer_class = DeliveryChallanSerializer
    permission_classes = [IsAuthenticated]

class PaymentReceiptListCreateView(generics.ListCreateAPIView):
    queryset = PaymentReceipt.objects.all().order_by('-created_at')
    serializer_class = PaymentReceiptSerializer
    permission_classes = [IsAuthenticated]



# core_app/views.py ke aakhir mein:

class ProductionJobListCreateView(generics.ListCreateAPIView):
    queryset = ProductionJob.objects.all().order_by('-created_at')
    serializer_class = ProductionJobSerializer
    permission_classes = [IsAuthenticated]

class ProductionJobRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductionJob.objects.all()
    serializer_class = ProductionJobSerializer
    permission_classes = [IsAuthenticated]



class JobMaterialReceiptListCreateView(generics.ListCreateAPIView):
    queryset = JobMaterialReceipt.objects.all().order_by('-created_at')
    serializer_class = JobMaterialReceiptSerializer
    permission_classes = [IsAuthenticated]

class JobPaymentRecordListCreateView(generics.ListCreateAPIView):
    queryset = JobPaymentRecord.objects.all().order_by('-created_at')
    serializer_class = JobPaymentRecordSerializer
    permission_classes = [IsAuthenticated]


# Views for Deleting History Records
class DeliveryChallanDestroyView(generics.DestroyAPIView):
    queryset = DeliveryChallan.objects.all()
    serializer_class = DeliveryChallanSerializer
    permission_classes = [IsAuthenticated]

class PaymentReceiptDestroyView(generics.DestroyAPIView):
    queryset = PaymentReceipt.objects.all()
    serializer_class = PaymentReceiptSerializer
    permission_classes = [IsAuthenticated]

class JobMaterialReceiptDestroyView(generics.DestroyAPIView):
    queryset = JobMaterialReceipt.objects.all()
    serializer_class = JobMaterialReceiptSerializer
    permission_classes = [IsAuthenticated]

class JobPaymentRecordDestroyView(generics.DestroyAPIView):
    queryset = JobPaymentRecord.objects.all()
    serializer_class = JobPaymentRecordSerializer
    permission_classes = [IsAuthenticated]


from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response

class DashboardStatsView(APIView):
    def get(self, request):
        # 1. Sales & Pending
        total_sales = SalesOrder.objects.aggregate(total=Sum('total_bill'))['total'] or 0
        total_received = SalesOrder.objects.aggregate(total=Sum('amount_received'))['total'] or 0
        client_pending = total_sales - total_received

        # 2. Production & Dues
        production_jobs = ProductionJob.objects.all()
        total_job_cost = sum(j.given_qty * j.job_rate_per_meter for j in production_jobs)
        total_paid_factory = ProductionJob.objects.aggregate(total=Sum('amount_paid'))['total'] or 0
        factory_dues = total_job_cost - total_paid_factory

        # 3. Low Stock Check
        low_stock_count = Product.objects.filter(stock_quantity__lt=50).count()

        return Response({
            "stats": {
                "total_sales": float(total_sales),
                "client_pending": float(client_pending),
                "factory_dues": float(factory_dues),
                "low_stock": low_stock_count
            },
            "sales_chart": [
                {"name": "Total Bill", "amt": float(total_sales)},
                {"name": "Received", "amt": float(total_received)},
                {"name": "Pending", "amt": float(client_pending)},
            ]
        })