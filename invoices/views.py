"""
VIEWS - The Business Logic Layer
Views receive HTTP requests, do work (DB queries, calculations),
and return HTTP responses (HTML pages or redirects).
Think of views as the "controllers" in MVC pattern.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Count, Sum, Q

from .models import Invoice, LineItem, ApprovalComment, UserProfile
from .forms import (
    LoginForm, InvoiceForm, LineItemFormSet,
    ApprovalForm, UserCreateForm
)
from .pdf_generator import generate_invoice_pdf


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_user_role(user):
    """Safely get role; default to 'employee' if profile missing."""
    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        return 'employee'


def require_role(*roles):
    """
    Decorator factory: wraps a view so only certain roles can access it.
    Usage: @require_role('admin', 'manager')
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if get_user_role(request.user) not in roles:
                return HttpResponseForbidden(
                    "<h2>Access Denied</h2><p>You don't have permission for this page.</p>"
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ─────────────────────────────────────────────
# AUTH VIEWS
# ─────────────────────────────────────────────

def login_view(request):
    """Handle GET (show form) and POST (process login) in one view."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # authenticate() checks username+password against the DB
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)  # Creates session cookie
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)  # Destroys session
    return redirect('login')


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

@login_required
def dashboard(request):
    """
    Main landing page after login.
    Shows different data depending on user role.
    """
    role = get_user_role(request.user)
    user = request.user

    # Admins/Managers see all invoices; employees see only their own
    if role in ['admin', 'manager']:
        all_invoices = Invoice.objects.select_related('created_by').all()
    else:
        all_invoices = Invoice.objects.filter(created_by=user)

    # Dashboard statistics cards
    stats = {
        'total':    all_invoices.count(),
        'draft':    all_invoices.filter(status='draft').count(),
        'pending':  all_invoices.filter(status='pending').count(),
        'approved': all_invoices.filter(status='approved').count(),
        'rejected': all_invoices.filter(status='rejected').count(),
    }

    # Recent 10 invoices for the table
    recent = all_invoices[:10]

    return render(request, 'invoices/dashboard.html', {
        'stats': stats,
        'recent': recent,
        'role': role,
    })


# ─────────────────────────────────────────────
# INVOICE CRUD
# ─────────────────────────────────────────────

@login_required
def invoice_list(request):
    """List all invoices with filtering by status."""
    role = get_user_role(request.user)
    status_filter = request.GET.get('status', '')

    if role in ['admin', 'manager']:
        invoices = Invoice.objects.select_related('created_by').all()
    else:
        invoices = Invoice.objects.filter(created_by=request.user)

    if status_filter:
        invoices = invoices.filter(status=status_filter)

    return render(request, 'invoices/invoice_list.html', {
        'invoices': invoices,
        'status_filter': status_filter,
        'role': role,
        'status_choices': Invoice.STATUS_CHOICES,
    })


@login_required
def invoice_create(request):
    """
    Create a new invoice with line items.
    Uses an InvoiceForm + a LineItemFormSet together in one page.
    The formset handles adding/removing multiple line items dynamically.
    """
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = LineItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            # Save invoice but don't commit to DB yet (commit=False)
            # This lets us set created_by before the final save
            invoice = form.save(commit=False)
            invoice.created_by = request.user

            # Check which button was pressed: Save Draft or Submit
            if 'submit_approval' in request.POST:
                invoice.status = 'pending'
            else:
                invoice.status = 'draft'

            invoice.save()  # Now actually write to database

            # Link the formset to this newly created invoice
            formset.instance = invoice
            formset.save()

            messages.success(request, f'Invoice {invoice.invoice_number} created!')
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
        formset = LineItemFormSet()

    return render(request, 'invoices/invoice_form.html', {
        'form': form,
        'formset': formset,
        'action': 'Create',
    })


@login_required
def invoice_edit(request, pk):
    """Edit an existing invoice. Only creator or admin can edit."""
    invoice = get_object_or_404(Invoice, pk=pk)
    role = get_user_role(request.user)

    # Permission check
    if invoice.created_by != request.user and role != 'admin':
        return HttpResponseForbidden("You cannot edit this invoice.")

    # Prevent editing approved invoices
    if invoice.status == 'approved' and role != 'admin':
        messages.error(request, 'Approved invoices cannot be edited.')
        return redirect('invoice_detail', pk=pk)

    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = LineItemFormSet(request.POST, instance=invoice)

        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            if 'submit_approval' in request.POST:
                invoice.status = 'pending'
            invoice.save()
            formset.save()
            messages.success(request, 'Invoice updated!')
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
        formset = LineItemFormSet(instance=invoice)

    return render(request, 'invoices/invoice_form.html', {
        'form': form,
        'formset': formset,
        'invoice': invoice,
        'action': 'Edit',
    })


@login_required
def invoice_detail(request, pk):
    """Show full invoice details + approval comments."""
    invoice = get_object_or_404(Invoice, pk=pk)
    role = get_user_role(request.user)
    comments = invoice.comments.select_related('user').all()

    # Pre-calculate totals for the template
    subtotal    = invoice.get_subtotal()
    tax_amount  = invoice.get_tax_amount()
    grand_total = invoice.get_grand_total()

    return render(request, 'invoices/invoice_detail.html', {
        'invoice': invoice,
        'comments': comments,
        'role': role,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'grand_total': grand_total,
    })


@login_required
def invoice_delete(request, pk):
    """Delete a draft invoice. Only creator or admin."""
    invoice = get_object_or_404(Invoice, pk=pk)
    role = get_user_role(request.user)

    if invoice.created_by != request.user and role != 'admin':
        return HttpResponseForbidden("You cannot delete this invoice.")

    if invoice.status not in ['draft', 'rejected'] and role != 'admin':
        messages.error(request, 'Only draft or rejected invoices can be deleted.')
        return redirect('invoice_detail', pk=pk)

    if request.method == 'POST':
        invoice_number = invoice.invoice_number
        invoice.delete()
        messages.success(request, f'Invoice {invoice_number} deleted.')
        return redirect('invoice_list')

    return render(request, 'invoices/invoice_confirm_delete.html', {'invoice': invoice})


# ─────────────────────────────────────────────
# APPROVAL WORKFLOW
# ─────────────────────────────────────────────

@login_required
def approve_invoice(request, pk):
    """Manager/Admin approves an invoice."""
    invoice = get_object_or_404(Invoice, pk=pk)
    role = get_user_role(request.user)

    if role not in ['admin', 'manager']:
        return HttpResponseForbidden("Only managers can approve invoices.")

    if invoice.status != 'pending':
        messages.error(request, 'Only pending invoices can be approved.')
        return redirect('invoice_detail', pk=pk)

    if request.method == 'POST':
        form = ApprovalForm(request.POST)
        if form.is_valid():
            invoice.status = 'approved'
            invoice.approved_by = request.user
            invoice.approved_at = timezone.now()
            invoice.save()

            # Save comment if provided
            comment_text = form.cleaned_data.get('comment', '').strip()
            if comment_text:
                ApprovalComment.objects.create(
                    invoice=invoice,
                    user=request.user,
                    comment=comment_text
                )

            # Auto-record approval action in comments
            ApprovalComment.objects.create(
                invoice=invoice,
                user=request.user,
                comment=f"✅ Invoice APPROVED by {request.user.get_full_name() or request.user.username}"
            )

            messages.success(request, f'Invoice {invoice.invoice_number} approved!')
            return redirect('invoice_detail', pk=pk)
    else:
        form = ApprovalForm()

    return render(request, 'invoices/approval_form.html', {
        'invoice': invoice,
        'form': form,
        'action': 'Approve'
    })


@login_required
def reject_invoice(request, pk):
    """Manager/Admin rejects an invoice."""
    invoice = get_object_or_404(Invoice, pk=pk)
    role = get_user_role(request.user)

    if role not in ['admin', 'manager']:
        return HttpResponseForbidden("Only managers can reject invoices.")

    if invoice.status != 'pending':
        messages.error(request, 'Only pending invoices can be rejected.')
        return redirect('invoice_detail', pk=pk)

    if request.method == 'POST':
        form = ApprovalForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data.get('comment', '').strip()
            if not reason:
                messages.error(request, 'Rejection reason is required.')
                return render(request, 'invoices/approval_form.html', {
                    'invoice': invoice, 'form': form, 'action': 'Reject'
                })

            invoice.status = 'rejected'
            invoice.rejection_reason = reason
            invoice.save()

            ApprovalComment.objects.create(
                invoice=invoice,
                user=request.user,
                comment=f"❌ Invoice REJECTED — Reason: {reason}"
            )

            messages.success(request, f'Invoice {invoice.invoice_number} rejected.')
            return redirect('invoice_detail', pk=pk)
    else:
        form = ApprovalForm()

    return render(request, 'invoices/approval_form.html', {
        'invoice': invoice,
        'form': form,
        'action': 'Reject'
    })


# ─────────────────────────────────────────────
# PDF GENERATION
# ─────────────────────────────────────────────

@login_required
def download_pdf(request, pk):
    """Generate and stream a PDF invoice to the browser."""
    invoice = get_object_or_404(Invoice, pk=pk)

    # Create an in-memory PDF using ReportLab
    buffer = generate_invoice_pdf(invoice)

    # HttpResponse with PDF content type streams the file directly
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
    return response


# ─────────────────────────────────────────────
# USER MANAGEMENT (Admin only)
# ─────────────────────────────────────────────

@require_role('admin')
def user_list(request):
    """Admin view: see all users and their roles."""
    users = User.objects.select_related('profile').all()
    return render(request, 'users/user_list.html', {'users': users})


@require_role('admin')
def user_create(request):
    """Admin creates a new user with a role."""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                department=form.cleaned_data.get('department', '')
            )
            messages.success(request, f"User '{user.username}' created.")
            return redirect('user_list')
    else:
        form = UserCreateForm()

    return render(request, 'users/user_form.html', {'form': form, 'action': 'Create'})


@require_role('admin')
def user_edit(request, pk):
    """Admin changes a user's role or department."""
    target_user = get_object_or_404(User, pk=pk)
    profile, _ = UserProfile.objects.get_or_create(user=target_user)

    if request.method == 'POST':
        role = request.POST.get('role', 'employee')
        dept = request.POST.get('department', '')
        profile.role = role
        profile.department = dept
        profile.save()
        messages.success(request, f"User '{target_user.username}' updated.")
        return redirect('user_list')

    return render(request, 'users/user_edit.html', {
        'target_user': target_user,
        'profile': profile,
        'roles': UserProfile.ROLE_CHOICES,
    })


# ─────────────────────────────────────────────
# CONTEXT PROCESSOR: status choices for templates
# ─────────────────────────────────────────────
# Add status_choices to invoice_list context
# (already in Invoice.STATUS_CHOICES but easier to access here)
