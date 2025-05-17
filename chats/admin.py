from django.contrib import admin
from .models import *
from django.contrib.admin import register

@register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ChatRoom._meta.fields]
    list_filter = ['slug' , 'is_private' ]
    search_fields = ['slug' , 'name' , 'created_by' , 'participants']
    list_per_page = 20

@register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Message._meta.fields if field.name not in ('content' , 'file')]
    list_per_page = 20
    search_fields = ['sender' , 'content' , 'sent_at' , 'room__name']

@register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DirectMessage._meta.fields if field.name not in ('created_at' , 'updated_at')]
    list_per_page = 20
    list_filter = ['is_read' , 'sent_at']
    search_fields = ['sender' , 'receiver' , 'content']


@register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MessageReaction._meta.fields if field.name not in ('created_at' , 'updated_at')]
    list_per_page = 20
    search_fields = ['message' , 'emoji' , 'user']
    list_display_links = ['message']