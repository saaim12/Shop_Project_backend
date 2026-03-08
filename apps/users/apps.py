from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    
    def ready(self):
        # Disconnect the create_permissions signal to avoid MongoDB compatibility issues
        from django.contrib.auth.management import create_permissions
        from django.db.models.signals import post_migrate
        post_migrate.disconnect(create_permissions, dispatch_uid="django.contrib.auth.management.create_permissions")