from django.contrib import admin
from .models import Invoice, LineItem, ApprovalComment, UserProfile

class LineItemInline(admin.TabularInline):
    model = LineItem
    extra = 1

class CommentInline(admin.TabularInline):
    model = ApprovalComment
    extra = 0
    readonly_fields = ['user', 'created_at']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display  = ['invoice_number', 'vendor_client', 'status', 'invoice_date', 'created_by']
    list_filter   = ['status', 'currency']
    search_fields = ['invoice_number', 'vendor_client', 'service_title']
    inlines       = [LineItemInline, CommentInline]

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department']
