"""
MODELS - The Database Layer
Think of models as blueprints. Each class = one database table.
Django auto-creates the SQL tables from these Python classes.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Invoice(models.Model):
    """
    Main invoice table. Stores every invoice created in the system.
    STATUS choices act like a state machine: draft → pending → approved/rejected
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    CURRENCY_CHOICES = [
        ('USD', 'USD - US Dollar'),
        ('EUR', 'EUR - Euro'),
        ('GBP', 'GBP - British Pound'),
        ('PKR', 'PKR - Pakistani Rupee'),
        ('INR', 'INR - Indian Rupee'),
    ]

    # Auto-generates unique invoice numbers like INV-2025-0001
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    
    # Who created this invoice
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_invoices'
    )
    
    # Vendor or client name (the "Issued To" in the image)
    vendor_client = models.CharField(max_length=200, verbose_name="Vendor / Client Name")
    vendor_email  = models.EmailField(blank=True, verbose_name="Vendor / Client Email")
    vendor_address = models.TextField(blank=True, verbose_name="Vendor / Client Address")
    
    # Service description (the "SERVICE TITLE" in the image)
    service_title = models.CharField(max_length=300, verbose_name="Service Title")
    notes = models.TextField(blank=True)
    
    # Dates
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    
    # Financial
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Tax percentage, e.g. 15 for 15%"
    )
    
    # Workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Approval tracking
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_invoices'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number} - {self.vendor_client}"

    def save(self, *args, **kwargs):
        """Auto-generate invoice number on first save."""
        if not self.invoice_number:
            year = timezone.now().year
            # Count existing invoices this year and increment
            count = Invoice.objects.filter(
                created_at__year=year
            ).count() + 1
            self.invoice_number = f"INV-{year}-{count:04d}"
        super().save(*args, **kwargs)

    def get_subtotal(self):
        """Sum all line item totals."""
        return sum(item.total for item in self.line_items.all())

    def get_tax_amount(self):
        """Calculate tax based on subtotal × tax_rate."""
        return (self.get_subtotal() * self.tax_rate) / 100

    def get_grand_total(self):
        """Final amount = subtotal + tax."""
        return self.get_subtotal() + self.get_tax_amount()


class LineItem(models.Model):
    """
    Each row in the invoice table (Description | Units | Price | Cost | Total).
    One invoice can have MANY line items — this is a one-to-many relationship.
    """
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name='line_items'
    )
    description = models.CharField(max_length=300)
    units = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total(self):
        """Calculated field: units × unit_price. Not stored in DB."""
        return self.units * self.unit_price

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
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def is_admin(self):
        return self.role == 'admin'

    def is_manager(self):
     return self.role in ['admin', 'manager']