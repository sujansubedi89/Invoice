"""
URL Configuration
Maps URL paths to view functions.
Think of this as the routing table for the entire app.
"""
from django.contrib import admin
from django.urls import path
from invoices import views

urlpatterns = [
    # Django admin panel (bonus: /admin/)
    path('admin/', admin.site.urls),

    # ── AUTH ──────────────────────────────────────────────────────────────
    path('',       views.login_view,  name='login'),
    path('login/', views.login_view,  name='login'),
    path('logout/',views.logout_view, name='logout'),

    # ── DASHBOARD ─────────────────────────────────────────────────────────
    path('dashboard/', views.dashboard, name='dashboard'),

    # ── INVOICES ──────────────────────────────────────────────────────────
    path('invoices/',              views.invoice_list,   name='invoice_list'),
    path('invoices/new/',          views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/',     views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/edit/',views.invoice_edit,   name='invoice_edit'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),

    # ── APPROVAL ──────────────────────────────────────────────────────────
    path('invoices/<int:pk>/approve/', views.approve_invoice, name='approve_invoice'),
    path('invoices/<int:pk>/reject/',  views.reject_invoice,  name='reject_invoice'),

    # ── PDF ───────────────────────────────────────────────────────────────
    path('invoices/<int:pk>/pdf/',     views.download_pdf,    name='download_pdf'),

    # ── USER MANAGEMENT ───────────────────────────────────────────────────
    path('users/',          views.user_list,   name='user_list'),
    path('users/new/',      views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
]
