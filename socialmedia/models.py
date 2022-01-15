from datetime import datetime 

from django.db import models 
from django.conf import settings
from django.db.models.deletion import CASCADE
from django.core.validators import MinLengthValidator 
# Create your models here.   

class Friend(models.Model): 
    account_id_1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend_account_1', on_delete=CASCADE)
    account_id_2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend_account_2', on_delete=CASCADE)
    date_confirmed = models.DateTimeField(auto_now_add=True)


class FriendRequest(models.Model):
    from_account = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend_request_from', on_delete=CASCADE)
    to_account = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend_request_to', on_delete=CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posts', on_delete=CASCADE)
    content = models.TextField(null=True)
    location = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Photos(models.Model):
    image_link = models.URLField()
    post = models.ForeignKey(Post, on_delete=CASCADE, related_name='photos')


class Like(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='likes', on_delete=CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments', on_delete=CASCADE)
    content = models.TextField()


class Share(models.Model):
    post = models.ForeignKey(Post, related_name='shares', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='shares', on_delete=CASCADE)
    shared_content = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)