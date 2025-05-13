from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import *
from django.db.models.signals import post_delete


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        AssetWatcher.objects.create(user=instance)



@receiver(post_delete, sender=AssetWatcher)
def delete_wordlist_file(sender, instance, **kwargs):
    if instance.wordlist and instance.wordlist.path:
        if os.path.isfile(instance.wordlist.path):
            os.remove(instance.wordlist.path)