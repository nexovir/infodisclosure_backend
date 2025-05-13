from django.apps import AppConfig


class PrivateWatchersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'private_watchers'

    def ready(self):
        import private_watchers.signals
        import private_watchers.signals

