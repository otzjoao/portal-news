from django.apps import AppConfig


class NoticiasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'noticias'

    def ready(self):
        from . import signals  # noqa: F401