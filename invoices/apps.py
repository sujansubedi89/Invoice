from django.apps import AppConfig

class InvoicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'invoices'

    def ready(self):
        from .init_users import create_demo_users

        try:
            create_demo_users()
        except:
            pass