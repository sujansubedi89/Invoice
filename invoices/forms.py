"""
FORMS - The Input Validation Layer
Forms validate user data before it touches the database.
Django forms are Python classes that map directly to HTML <form> elements.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Invoice, LineItem, UserProfile


class LoginForm(forms.Form):
    """Simple login form with styled widgets."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input', 'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input', 'placeholder': 'Password'
        })
    )


class InvoiceForm(forms.ModelForm):
    """
    ModelForm = Django inspects the Invoice model and auto-builds
    form fields matching the model fields. We just customize widgets.
    """
    class Meta:
        model = Invoice
        fields = [
            'vendor_client', 'vendor_email', 'vendor_address',
            'service_title', 'invoice_date', 'due_date',
            'currency', 'tax_rate', 'notes'
        ]
        widgets = {
            'vendor_client':   forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Client / Vendor name'}),
            'vendor_email':    forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'client@email.com'}),
            'vendor_address':  forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Full address'}),
            'service_title':   forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Web scraping service for Jake Robinson'}),
            'invoice_date':    forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'due_date':        forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'currency':        forms.Select(attrs={'class': 'form-input'}),
            'tax_rate':        forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'max': '100'}),
            'notes':           forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Additional notes or terms...'}),
        }


class LineItemForm(forms.ModelForm):
    class Meta:
        model = LineItem
        fields = ['description', 'unit_type', 'units', 'unit_price']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-input li-desc', 'placeholder': 'Service description'}),
            'unit_type':   forms.Select(attrs={'class': 'form-input li-type'}),
            'units':       forms.NumberInput(attrs={'class': 'form-input li-units', 'step': '0.01', 'min': '0', 'value': '1'}),
            'unit_price':  forms.NumberInput(attrs={'class': 'form-input li-price', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
        }


# Django Formset: a collection of the same form that can be submitted together.
# extra=1 means show 1 empty row by default; can_delete=True adds a delete checkbox.
LineItemFormSet = forms.inlineformset_factory(
    Invoice, LineItem,
    form=LineItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class ApprovalForm(forms.Form):
    """Used by managers to approve or reject with a comment."""
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input', 'rows': 3,
            'placeholder': 'Add a comment (required for rejection)...'
        })
    )


class UserCreateForm(UserCreationForm):
    """Extends Django's built-in registration form to include role."""
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Department'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not hasattr(field.widget, 'attrs'):
                continue
            field.widget.attrs.setdefault('class', 'form-input')
