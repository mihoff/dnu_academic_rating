from django.apps import AppConfig


class SystemAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'system_app'
    verbose_name = 'Системні дані'
