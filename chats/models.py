from django.db import models
from users.models import BaseModel
from django.contrib.auth.models import User
import uuid


class ChatRoom(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_private = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='chatrooms')

    def __str__(self):
        return f"{self.created_by} - {self.name}"

    class Meta :
        verbose_name = 'ChatRoom'
        verbose_name_plural = 'ChatRooms'



class Message(BaseModel):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__ (self) :
        return f"{self.room} - {self.sender}"
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'



class DirectMessage(BaseModel):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    file = models.FileField(upload_to='direct_files/', null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} - {self.receiver}"
    
    class Meta : 
        verbose_name = 'DirectMessage'
        verbose_name_plural = 'DirectMessages'



class MessageReaction(BaseModel):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10)  # مثل 👍 ❤️ 🔥 😂
    reacted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.emoji}"
    
    class Meta:
        unique_together = ('message', 'user', 'emoji')
