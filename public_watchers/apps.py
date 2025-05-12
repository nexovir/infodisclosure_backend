from django.apps import AppConfig


class WatchersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'public_watchers'

    def ready(self):
        import public_watchers.tasks
        