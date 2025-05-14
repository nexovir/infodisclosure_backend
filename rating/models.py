from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from users.models import BaseModel

RATING_CHOICES = [
    (1, 'Very Poor'),
    (2, 'Poor'),
    (3, 'Average'),
    (4, 'Good'),
    (5, 'Excellent'),
]

class Rating(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)

    # Generic relation to Tool, Technique, or ZeroDay
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


    class Meta:
        unique_together = ('user', 'content_type', 'object_id')  # Prevent duplicate ratings
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} rated {self.content_object} as {self.score}"
