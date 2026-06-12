"""
MODELS - The Database Layer
Think of models as blueprints. Each class = one database table.
Django auto-creates the SQL tables from these Python classes.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

import uuid


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    CURRENCY_CHOICES = [
        ('NPR','NPR-Nepali Rupee'),
        ('USD', 'USD - US Dollar'),
        ('EUR', 'EUR - Euro'),
        ('GBP', 'GBP - British Pound'),
        ('PKR', 'PKR - Pakistani Rupee'),
        ('INR', 'INR - Indian Rupee'),
    ]

    invoice_number  = models.CharField(max_length=50, unique=True, blank=True)
    created_by      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_invoices')
    vendor_client   = models.CharField(max_length=200, verbose_name="Vendor / Client Name")
    vendor_email    = models.EmailField(blank=True, verbose_name="Vendor / Client Email")
    vendor_address  = models.TextField(blank=True, verbose_name="Vendor / Client Address")
    service_title   = models.CharField(max_length=300, verbose_name="Service Title")
    notes           = models.TextField(blank=True)
    invoice_date    = models.DateField(default=timezone.now)
    due_date        = models.DateField(null=True, blank=True)
    currency        = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    tax_rate        = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                          help_text="Tax percentage, e.g. 15 for 15%")
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    approved_by     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                          related_name='approved_invoices')
    approved_at     = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number} - {self.vendor_client}"

    def save(self, *args, **kwargs):          # ← 4-space indent, INSIDE the class
        if not self.invoice_number:
            year = timezone.now().year
            last_invoice = (
                Invoice.objects.filter(invoice_number__startswith=f"INV-{year}-")
                .order_by("-id")
                .first()
            )
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split("-")[-1])
                next_number = last_number + 1
            else:
                next_number = 1
            self.invoice_number = f"INV-{year}-{next_number:04d}"
        super().save(*args, **kwargs)

    def get_subtotal(self):                   # ← also INSIDE the class
        return sum(item.total for item in self.line_items.all())

    def get_tax_amount(self):
        return (self.get_subtotal() * self.tax_rate) / 100

    def get_grand_total(self):
        return self.get_subtotal() + self.get_tax_amount()


class LineItem(models.Model):
    """
    Each row in the invoice table (Description | Units | Price | Cost | Total).
    One invoice can have MANY line items — this is a one-to-many relationship.
    """
    DURATION_CHOICES = [
        ('fixed',   'Fixed Price'),
        ('hourly',  'Per Hour'),
        ('daily',   'Per Day'),
        ('monthly', 'Per Month'),
    ]
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name='line_items'
    )
    description = models.CharField(max_length=300)
    units = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_type   = models.CharField(max_length=10, choices=DURATION_CHOICES, default='fixed')

    @property
    def total(self):
        result = self.units * self.unit_price
        return result.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def __str__(self):
        return f"{self.description} x{self.units}"


class ApprovalComment(models.Model):
    """
    Audit trail: every comment/action taken during the approval process.
    This gives managers a history of who said what and when.
    """
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name='comments'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.invoice.invoice_number}"


class UserProfile(models.Model):
    """
    Extends Django's built-in User with a role field.
    Django's User handles passwords/auth; we handle roles here.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
        ('guest','Guest')
    ]
    # "Guest"
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def is_admin(self):
        return self.role == 'admin'
    def is_guest(self):
        return self.role=='guest'

    def is_manager(self):
     return self.role in ['admin', 'manager']
    


































class PaymentDetails(models.Model):

    PAYMENT_TYPE_CHOICES=[
        ('paypal','PayPal'),
        ('bank','Bank Transfer'),]
    invoice=models.OneToOneField(
        
            Invoice,on_delete=models.CASCADE,related_name='payment_details'

        )
    payment_type=models.CharField(
        max_length=10,choices=PAYMENT_TYPE_CHOICES,default='paypal'
    )
    paypal_email=models.EmailField(blank=True)
    bank_name=models.CharField(max_length=100,blank=True)
    account_number=models.CharField(max_length=90,blank=True)
    account_holder=models.CharField(max_length=90,blank=True)
    routing_number=models.CharField(max_length=50,blank=True)
    
    swift_code=models.CharField(max_length=20,blank=True)
    def __str__(self):
        return f"Payment details for {self.invoice.invoice_number}"