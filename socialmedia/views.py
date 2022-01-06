from datetime import date

from django.db import transaction
from django.db.models.aggregates import Count
from django.db.models.query import Prefetch
from django.contrib.auth import get_user_model
from rest_framework.decorators import authentication_classes

from core import models
from .models import Comment, Friend, FriendRequest, Like, Post, Share 
from .serializers import CreateCommentSerializer, CreatePostLikeSerializer, \
    CreatePostShareSerializer, FriendRequestSerializer, FriendsSerializer, \
    PostCommentSerializer, PostCreateSerializer, PostLikesSerializer, \
    PostSerializer, PostShareSerializer, SendFriendRequestSerializer

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response 
from rest_framework import serializers, status
import cloudinary

class Timeline(ViewSet):
    
    def list(self, request):
        posts = Post.objects\
        .select_related('user') \
        .prefetch_related('photos', 'likes', 'comments', 'shares').annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments'),
            shares_count=Count('shares')
        ).all()

        shared_posts = Share.objects.select_related('user')\
            .prefetch_related(
                Prefetch('post', queryset=Post.objects.annotate(
                likes_count=Count('likes'),
                comments_count=Count('comments'),
                shares_count=Count('shares'),
            )), 'post__photos').all()
        
        post_serializer = PostSerializer(posts, many=True)

        shared_posts_serializer = PostShareSerializer(shared_posts, many=True)
        data = post_serializer.data + shared_posts_serializer.data
        
        return Response(data, status=status.HTTP_200_OK)

# Create your views here.
class Posts(ModelViewSet):  
    queryset = Post.objects\
        .select_related('user') \
        .prefetch_related('photos')\
        .annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments'),
            shares_count=Count('shares'),
        )\
        .all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer

        return PostSerializer

    def get_serializer_context(self):
        return {
            'user_id': self.request.user.id, 
        }

    def create(self, request, *args, **kwargs):
        res = cloudinary.uploader.upload(self.request.FILES.getlist('photos')[0])
        print(res)
        return super().create(request, *args, **kwargs)

    

class PostLikes(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self): 
        return Like.objects.select_related('user').filter(post_id=self.kwargs['post_pk']).all()

    def get_serializer_class(self): 
        if self.request.method == 'POST':
            return CreatePostLikeSerializer
        return PostLikesSerializer

    def get_serializer_context(self):
        return {
            'user_id': self.request.user.id,
            'post_id': self.kwargs['post_pk']
        }

    def create(self, request, *args, **kwargs):
        if Like.objects.filter(post_id=kwargs['post_pk'], user_id=self.request.user.id).exists():
            Like.objects.filter(post_id=kwargs['post_pk'], user_id=self.request.user.id).delete()
            return Response({'message': "Liked removed successfully"}, status=status.HTTP_204_NO_CONTENT)

        return super().create(request, *args, **kwargs)


class PostComments(ModelViewSet):
    serializer_class = PostCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self): 
        return Comment.objects.select_related('user').filter(post_id=self.kwargs['post_pk']).all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateCommentSerializer

        return PostCommentSerializer

    def get_serializer_context(self):
        return {
            'user_id': self.request.user.id,
            'post_id': self.kwargs['post_pk']
        }


class PostShares(ModelViewSet):
    serializer_class = PostShareSerializer

    def get_queryset(self):
        return Share.objects.prefetch_related('user', 'post').filter(post_id=self.kwargs['post_pk']).all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreatePostShareSerializer
        return PostShareSerializer

    def get_serializer_context(self):
        return {
            'user_id': self.request.user.id,
            'post_id': self.kwargs['post_pk']
        }


class Friends(ModelViewSet):
    serializer_class = FriendsSerializer
    
    def get_queryset(self):
        return Friend.objects.prefetch_related('account_id_1', 'account_id_2').all()


class FriendRequests(ModelViewSet):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.select_related('from_account','to_account').all()

    def get_serializer_context(self):
        return {
            'from_account_id': self.request.user.id, 
        }

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SendFriendRequestSerializer
        return FriendRequestSerializer

    
    def create(self, request, *args, **kwargs):
        friend_request = {
            'from_account' : self.request.user.id, \
            'to_account': self.request.data['to_account']
        }

        if Friend.objects.filter(account_id_1=friend_request['from_account'] , \
             account_id_2=friend_request['to_account']).exists():

            return Response({'message': 'You guys are already friends!'}, \
            status=status.HTTP_400_BAD_REQUEST)
        
        elif FriendRequest.objects.filter(from_account_id=friend_request['from_account'], \
            to_account_id=friend_request['to_account']).exists():
            
            return Response({'message': 'You have already sent a friend request to this user!'}, \
            status=status.HTTP_400_BAD_REQUEST)

        elif friend_request['from_account'] == friend_request['to_account']:
            return Response({'message': 'Please provide valid values'}, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        is_request_accepted = self.request.GET.get('is_accepted')
        friend = get_user_model().objects.filter(email=instance.to_account).first()

        if is_request_accepted == 'true':            
            with transaction.atomic():
                account_one = Friend(account_id_1=instance.from_account, \
                    account_id_2=instance.to_account)
                account_two = Friend(account_id_1=instance.to_account, \
                    account_id_2=instance.from_account)
                Friend.objects.bulk_create([account_one, account_two])
                instance.delete()
                return Response({'message': f'You are now a friend of {friend.first_name} {friend.last_name}'}, status=status.HTTP_204_NO_CONTENT)
        
        elif is_request_accepted == 'false':
            instance.delete()
            return Response({'message': 'Request Deleted Successfully'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'Status of friend request not found!'}, status=status.HTTP_400_BAD_REQUEST)