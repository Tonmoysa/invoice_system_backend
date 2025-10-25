from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Invoice, Transaction
from .serializers import InvoiceSerializer, InvoiceListSerializer, PaymentSerializer


class InvoiceListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return InvoiceListSerializer
        return InvoiceSerializer
    
    def get_queryset(self):
        return Invoice.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceSerializer
    
    def get_queryset(self):
        return Invoice.objects.filter(created_by=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_invoice_paid(request, pk):
    """
    Mark an invoice as paid and create a payment transaction
    """
    invoice = get_object_or_404(Invoice, pk=pk, created_by=request.user)
    
    if invoice.status != 'pending':
        return Response(
            {'error': 'Only pending invoices can be marked as paid'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = PaymentSerializer(data=request.data, context={'invoice': invoice})
    if serializer.is_valid():
        with transaction.atomic():
            # Update invoice status
            invoice.status = 'paid'
            invoice.save()
            
            # Create payment transaction
            Transaction.objects.create(
                transaction_type='payment',
                amount=serializer.validated_data['amount'],
                description=serializer.validated_data['description'],
                invoice=invoice,
                created_by=request.user
            )
        
        return Response({'message': 'Invoice marked as paid successfully'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoice_statistics(request):
    """
    Get basic statistics for the user's invoices
    """
    user_invoices = Invoice.objects.filter(created_by=request.user)
    
    stats = {
        'total_invoices': user_invoices.count(),
        'pending_invoices': user_invoices.filter(status='pending').count(),
        'paid_invoices': user_invoices.filter(status='paid').count(),
        'total_revenue': sum(invoice.total_amount for invoice in user_invoices.filter(status='paid')),
        'pending_amount': sum(invoice.total_amount for invoice in user_invoices.filter(status='pending')),
    }
    
    return Response(stats)
