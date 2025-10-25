from rest_framework import serializers
from decimal import Decimal
from django.core.validators import MinValueValidator
from .models import Invoice, InvoiceItem, Transaction


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'total_price']
        read_only_fields = ['total_price']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'amount', 'description', 'created_at']
        read_only_fields = ['created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, required=False)
    transactions = TransactionSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'customer_name', 'customer_email', 
            'customer_address', 'status', 'total_amount', 'created_at', 
            'updated_at', 'created_by', 'items', 'transactions'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_amount']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        invoice = Invoice.objects.create(**validated_data)
        
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        
        # Create sale transaction
        Transaction.objects.create(
            transaction_type='sale',
            amount=invoice.total_amount,
            description=f'Sale for invoice {invoice.invoice_number}',
            invoice=invoice,
            created_by=invoice.created_by
        )
        
        return invoice
    
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        # Update invoice fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update items if provided
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                InvoiceItem.objects.create(invoice=instance, **item_data)
        
        return instance


class InvoiceListSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'customer_name', 'customer_email',
            'status', 'total_amount', 'created_at', 'created_by', 'items_count'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()


class PaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    description = serializers.CharField(max_length=200, required=False, default='Payment received')
    
    def validate_amount(self, value):
        invoice = self.context['invoice']
        if value > invoice.total_amount:
            raise serializers.ValidationError("Payment amount cannot exceed invoice total")
        return value
