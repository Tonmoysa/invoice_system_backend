from django.urls import path
from . import views

urlpatterns = [
    path('invoices/', views.InvoiceListCreateView.as_view(), name='invoice-list-create'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice-detail'),
    path('invoices/<int:pk>/pay/', views.mark_invoice_paid, name='invoice-pay'),
    path('statistics/', views.invoice_statistics, name='invoice-statistics'),
]
