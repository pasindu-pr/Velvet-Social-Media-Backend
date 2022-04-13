from dataclasses import fields
from datetime import date
from itertools import chain
from pyexpat import model
from re import T
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Value
from django.db.models.aggregates import Count
from django.db.models.query import Prefetch

from rest_framework.serializers import URLField
from rest_framework import serializers
from rest_framework.fields import BooleanField, CharField, ImageField, SerializerMethodField 

from .models import Comment, Friend, FriendRequest, Like, Photos, Post, Share

from cloudinary.models import CloudinaryField

class SocialUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model() 
        fields = ['id', 'profile_picture', 'full_name', 'location']

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'


class PostPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photos
        fields = ['id', 'image_link']


class PostLikesSerializer(serializers.ModelSerializer):
    user = SocialUserSerializer()

    class Meta:
        model = Like
        fields = ['id', 'user']


class CreatePostLikeSerializer(serializers.ModelSerializer): 
    id = serializers.ReadOnlyField()
    user = SocialUserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user']

    def create(self, validated_data):
        instance = Like(post_id=self.context['post_id'], user_id=self.context['user_id'])
        instance.save()
        return instance


class PostCommentSerializer(serializers.ModelSerializer):
    user = SocialUserSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']



class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']

    def create(self, validated_data):
        comment = Comment(user_id=self.context['user_id'], post_id=self.context['post_id'] ,**validated_data)
        comment.save()
        return comment


class PostSerializer(serializers.ModelSerializer):
    photos = PostPhotoSerializer(many=True)
    likes_count = serializers.IntegerField()
    comments_count = serializers.IntegerField()
    shares_count = serializers.IntegerField()
    user = SocialUserSerializer() 
    likes = PostLikesSerializer(many=True)

    class Meta:
        model = Post
        fields = ['id', 'content', 'location' ,'user', 'photos', \
             'likes', 'likes_count', 'comments_count', 'shares_count', 'created_at']


class TimelinePostShareSerializer(serializers.ModelSerializer):
    user = SocialUserSerializer()
    post = PostSerializer()
    is_shared_post = BooleanField()

    class Meta:
        model = Share
        fields = ['id', 'user', 'post', 'is_shared_post' ,'shared_content', 'created_at'] 


class PostShareSerializer(serializers.ModelSerializer):
    user = SocialUserSerializer()
    post = PostSerializer() 
    class Meta:
        model = Share
        fields = ['id', 'user', 'post','shared_content', 'created_at'] 


class CreatePostShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share
        fields = ['shared_content']

    def create(self, validated_data):
        instance = Share(user_id=self.context['user_id'], \
            post_id=self.context['post_id'], **validated_data)
        instance.save()
        return instance


class PostCreateSerializer(serializers.ModelSerializer):
    image = URLField()

    class Meta:
        model = Post
        fields = ['content', 'location', 'image']

    def create(self, validated_data):
        post = Post(user_id=self.context['user_id'], **validated_data)
        post.save()
        return post


class FriendsSerializer(serializers.ModelSerializer):
    account_id_2 = SocialUserSerializer()

    class Meta:
        model = Friend
        fields = ['id', 'account_id_2', 'date_confirmed']


class FriendRequestSerializer(serializers.ModelSerializer):
    from_account = SocialUserSerializer()
    to_account = SocialUserSerializer()

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_account', 'to_account', 'request_date']


class SendFriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['to_account']   

    def create(self, validated_data):
        instance = FriendRequest(from_account_id=self.context['from_account_id'], **validated_data)
        instance.save()
        return instance


class AcceptOrRejectFriendRequestSerializer(serializers.ModelSerializer):  
    class Meta:
        model = FriendRequest
        fields = ['id']
 
class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photos
        fields = ['id', 'image_link'] 


class UserProfileDetailsSerializer(serializers.ModelSerializer):
    friends = serializers.SerializerMethodField() 
    photos = PhotoSerializer(many=True) 
    posts = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'location', 'profile_picture', \
            'website', 'description', 'friends', 'photos', 'posts']

    def get_posts(self, obj): 
        shared_posts_serializer = TimelinePostShareSerializer(Share.objects.filter(user_id=self.context['user_id'])\
            .select_related('user')\
            .prefetch_related(
                Prefetch('post', queryset=Post.objects.annotate(
                likes_count=Count('likes', distinct=True),
                comments_count=Count('comments', distinct=True),
                shares_count=Count('shares', distinct=True),
            )), 'post__photos', 'post__user', 'post__likes', 'post__likes__user').annotate(
                is_shared_post=Value(True), 
            ).all() , many=True)


        post_serializer = PostSerializer(Post.objects.filter(user_id=self.context['user_id']).select_related('user')\
                .prefetch_related('photos', 'likes', 'likes__user').annotate(likes_count=Count('likes', distinct=True), comments_count=Count('comments',  distinct=True),
                shares_count=Count('shares', distinct=True)).order_by('-created_at').all(), many=True)

        data = sorted(chain(post_serializer.data, shared_posts_serializer.data),key = lambda i: i['created_at'], reverse=True)  
        return data

    def get_friends(self, obj):
            return Friend.objects.filter(account_id_1=self.context['user_id']).count()