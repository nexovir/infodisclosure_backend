from django.apps import AppConfig


class WatchersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'watchers'

    def ready(self):
        import watchers.tasks
        