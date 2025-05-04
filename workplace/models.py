from django.db import models
from django.contrib.auth.models import User
from users.models import BaseModel



class Workplace(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='workplace')
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True , default=None)

    logo = models.ImageField(upload_to="workplace/logos/", blank=True, null=True)
    banner = models.ImageField(upload_to="workplace/banners/", blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.owner.username}"
    
    class Meta :
        verbose_name = 'workplace'
        verbose_name_plural = 'workplaces'
        ordering = ['-id']

