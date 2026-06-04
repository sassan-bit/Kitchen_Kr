from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'kitchen', 'rating', 'created_at')
    list_filter = ('created_at', 'rating')
    search_fields = ('user__username', 'kitchen__name')