from django.contrib import admin
from .models import Comment, Like, Post, Share
# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'content', 'location', 'created_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id' ,'post_id']


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ['id' ,'post_id']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id' ,'post_id']