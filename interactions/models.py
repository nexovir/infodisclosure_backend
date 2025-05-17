from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from users.models import BaseModel
from django.contrib.auth.models import User

class Like(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__ (self):
        return f"{self.user} - {self.content_type} - {self.content_object}"

    class Meta : 
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
        unique_together = ('user', 'content_type', 'object_id')


        
class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    text = models.TextField()

    def __str__ (self):
        return f"{self.user} - {self.content_type} - {self.content_object}"

    class Meta : 
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
