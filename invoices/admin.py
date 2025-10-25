from django.contrib import admin
from .models import Invoice, InvoiceItem, Transaction


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer_name', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['invoice_number', 'customer_name', 'customer_email']
    inlines = [InvoiceItemInline, TransactionInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_type', 'amount', 'invoice', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['invoice__invoice_number', 'description']
    readonly_fields = ['created_at']