from django.contrib import admin
from .models import Comment, Friend, Like, Photos, Post, Share
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

@admin.register(Photos)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'image_link', 'post', 'user']

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ['id', 'account_id_1','account_id_2', 'date_confirmed']