from django.contrib import admin
from .models import Rating
from django.contrib.contenttypes.admin import GenericTabularInline


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_object', 'score', 'created_at', 'updated_at')
    list_filter = ('score', 'created_at')
    search_fields = ('user__username', 'comment')
    readonly_fields = ('created_at', 'updated_at')

    # برای نمایش فیلد Generic ForeignKey
    def content_object(self, obj):
        return f"{obj.content_type.name} - ID:{obj.object_id}"

    content_object.short_description = "Rated Object"
