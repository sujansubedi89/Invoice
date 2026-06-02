# Jyaba Tech — Invoice Management System
## Django 4.x · SQLite · ReportLab PDF · Pure HTML Templates

---

## Quick Start (3 commands)

```bash
# 1. Install dependencies
pip install django reportlab pillow

# 2. Set up database + demo data
python manage.py migrate
python manage.py shell < seed_data.py   # OR use createsuperuser

# 3. Run server
python manage.py runserver
```
Visit: http://127.0.0.1:8000

---

## Demo Accounts

| Username   | Password  | Role     |
|------------|-----------|----------|
| admin      | demo1234  | Admin    |
| surendra   | demo1234  | Manager  |
| tara       | demo1234  | Manager  |
| roshan     | demo1234  | Manager  |
| sujan      | demo1234  | Employee |

---

## Project Structure

```
invoice_system/
├── invoice_system/         # Django project config
│   ├── settings.py         # All configuration
│   └── urls.py             # Route map
├── invoices/               # Main app
│   ├── models.py           # Database tables (Invoice, LineItem, etc.)
│   ├── views.py            # Business logic
│   ├── forms.py            # Input validation
│   ├── urls.py             # (moved to invoice_system/urls.py)
│   ├── pdf_generator.py    # ReportLab PDF builder
│   ├── signals.py          # Auto-create UserProfile
│   └── admin.py            # Django admin config
├── templates/              # HTML templates
│   ├── base.html           # Master layout with sidebar
│   ├── auth/login.html
│   ├── invoices/
│   │   ├── dashboard.html
│   │   ├── invoice_list.html
│   │   ├── invoice_form.html   # Create + Edit
│   │   ├── invoice_detail.html # Live invoice preview
│   │   └── approval_form.html
│   └── users/
│       ├── user_list.html
│       ├── user_form.html
│       └── user_edit.html
└── static/css/main.css     # All styles
```

---

## Key Concepts

### 1. Models = Database Tables
`models.py` defines Python classes; Django converts them to SQL automatically.

### 2. Formsets = Multiple Forms Together
`LineItemFormSet` in `forms.py` lets users add/remove invoice rows dynamically.

### 3. Role-Based Access
`require_role()` decorator in `views.py` protects routes.
Roles: admin > manager > employee.

### 4. PDF Generation
`pdf_generator.py` uses ReportLab to draw the invoice to a BytesIO buffer,
which is streamed directly to the browser as a download.

### 5. Approval Workflow
Status machine: draft → pending → approved / rejected
Only managers/admins can approve. All actions are logged in ApprovalComment.
