from django.urls import path
from . import views
from .views import PartyListCreateView, SalesOrderListCreateView, SalesOrderRetrieveUpdateDestroyView 
from .views import PartyListCreateView, SalesOrderListCreateView, SalesOrderRetrieveUpdateDestroyView, DeliveryChallanListCreateView, PaymentReceiptListCreateView
from .views import ProductionJobListCreateView, ProductionJobRetrieveUpdateDestroyView
from .views import JobMaterialReceiptListCreateView, JobPaymentRecordListCreateView, DashboardStatsView
from .views import DeliveryChallanDestroyView, PaymentReceiptDestroyView, JobMaterialReceiptDestroyView, JobPaymentRecordDestroyView

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('api/parties/', PartyListCreateView.as_view(), name='party-list'),
    path('api/sales-orders/', SalesOrderListCreateView.as_view(), name='sales-order-list'),
    path('api/sales-orders/<int:pk>/', SalesOrderRetrieveUpdateDestroyView.as_view(), name='sales-order-detail'),
    path('api/challans/', DeliveryChallanListCreateView.as_view(), name='challan-list-create'),
    path('api/receipts/', PaymentReceiptListCreateView.as_view(), name='receipt-list-create'),
    path('api/production-jobs/', ProductionJobListCreateView.as_view(), name='production-job-list'),
    path('api/production-jobs/<int:pk>/', ProductionJobRetrieveUpdateDestroyView.as_view(), name='production-job-detail'),
    path('api/job-materials/', JobMaterialReceiptListCreateView.as_view(), name='job-material-list'),
    path('api/job-payments/', JobPaymentRecordListCreateView.as_view(), name='job-payment-list'),
    path('api/challans/<int:pk>/', DeliveryChallanDestroyView.as_view(), name='challan-delete'),
    path('api/receipts/<int:pk>/', PaymentReceiptDestroyView.as_view(), name='receipt-delete'),
    path('api/job-materials/<int:pk>/', JobMaterialReceiptDestroyView.as_view(), name='job-material-delete'),
    path('api/job-payments/<int:pk>/', JobPaymentRecordDestroyView.as_view(), name='job-payment-delete'),
    path('api/dashboard-stats/', DashboardStatsView.as_view())
]   