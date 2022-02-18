from itertools import chain
from django.db.models import Value, Case, When, BooleanField,Subquery
from re import T 

from django.db import transaction
from django.db.models.aggregates import Count
from django.db.models.query import Prefetch
from django.contrib.auth import get_user_model
from markupsafe import re
from rest_framework.fields import FileField

from core import models
from .models import Comment, Friend, FriendRequest, Like, Photos, Post, Share, TemporayImages 
from .serializers import CreateCommentSerializer, CreatePostLikeSerializer, \
    CreatePostShareSerializer, FriendRequestSerializer, FriendsSerializer, PhotoSerializer, \
    PostCommentSerializer, PostCreateSerializer, PostLikesSerializer, \
    PostSerializer, PostShareSerializer, SendFriendRequestSerializer,\
        TimelinePostShareSerializer

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response 
from rest_framework import status 
from rest_framework.mixins import CreateModelMixin, \
     DestroyModelMixin, ListModelMixin, RetrieveModelMixin

from cloudinary.uploader import upload as CloudinaryUpload

from pprint import pprint

class Timeline(ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        # Find current user's friends and convert get friends ids
        friends_queryset = Friend.objects.filter(account_id_1=self.request.user.id)\
                  .all() 
        
        user_friends = [item.account_id_2 for item in list(friends_queryset)] 

        posts_queryset = Post.objects.filter(user_id__in=user_friends)\
                .select_related('user')\
                .prefetch_related('photos', 'likes', 'likes__user').annotate(likes_count=Count('likes', distinct=True), comments_count=Count('comments',  distinct=True),
                shares_count=Count('shares', distinct=True)).order_by('-created_at').all()
               
        shared_posts_queryset = Share.objects.filter(user_id__in=user_friends)\
            .select_related('user')\
            .prefetch_related(
                Prefetch('post', queryset=Post.objects.annotate(
                likes_count=Count('likes', distinct=True),
                comments_count=Count('comments', distinct=True),
                shares_count=Count('shares', distinct=True),
            )), 'post__photos', 'post__user', 'post__likes', 'post__likes__user').annotate(
                is_shared_post=Value(True), 
            ).all()
        
        post_serializer = PostSerializer(posts_queryset, many=True)
        shared_posts_serializer = TimelinePostShareSerializer(shared_posts_queryset, many=True)

        data = sorted(chain(post_serializer.data, shared_posts_serializer.data),key = lambda i: i['created_at'], reverse=True)  
        # data = sorted(post_serializer.data, key = lambda i: i['created_at'], reverse=True)
        return Response(data, status=status.HTTP_200_OK) 


# Create your views here.
class Posts(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Post.objects\
            .select_related('user') \
            .prefetch_related('photos', 'likes', 'likes__user')\
            .annotate(
                likes_count=Count('likes'),
                comments_count=Count('comments'),
                shares_count=Count('shares'),\
            )\
            .all()
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer

        return PostSerializer

    def get_serializer_context(self):
        return {
            'user_id': self.request.user.id, 
        }

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            res = CloudinaryUpload(self.request.FILES['photos'], folder="/VelvetSocialMedia/")
            content = self.request.POST.get("content")
            location = self.request.POST.get("content")  
            post = Post(content=content, location=location, user_id=self.request.user.id)
            post.save() 
            photo = Photos(image_link=res['secure_url'], post_id=post.id) 
            photo.save()
            return Response({"message": "Post created successfully!"}, status=status.HTTP_201_CREATED)
 
     
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
        return Share.objects.filter(post_id=self.kwargs['post_pk'])\
            .select_related('user')\
            .prefetch_related(
                Prefetch('post', queryset=Post.objects.annotate(
                likes_count=Count('likes'),
                comments_count=Count('comments'),
                shares_count=Count('shares'),
            )), 'post__photos', 'post__user').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreatePostShareSerializer
        return PostShareSerializer

    def get_serializer_context(self):
        return {
            'user_id': self.request.user.id,
            'post_id': self.kwargs['post_pk']
        }


class PostPhotos(ListModelMixin, GenericViewSet): 
    def get_serializer_class(self): 
        return PhotoSerializer

    def get_queryset(self): 
        return Photos.objects.filter(post_id=self.kwargs['post_pk']).all();


class Friends(ListModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = FriendsSerializer
    
    def get_queryset(self):
        return Friend.objects.select_related('account_id_2')\
        .filter(account_id_1=self.request.user.id).all()

    def destroy(self, request, *args, **kwargs):
        friend_query_set = Friend.objects.filter(id=kwargs['pk']).first()

        # Find other user's friend and delete record
        with transaction.atomic():
            Friend.objects.filter(account_id_1=self.request.user.id, \
                account_id_2=friend_query_set.account_id_2).delete()

            Friend.objects.filter(account_id_1=friend_query_set.account_id_2, \
                account_id_2=self.request.user.id).delete()

        return Response(f'User unfriended successfully!')


class FriendRequests(CreateModelMixin,ListModelMixin ,RetrieveModelMixin, DestroyModelMixin,GenericViewSet):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(to_account=self.request.user.id).select_related('from_account','to_account').all()

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


@api_view(["POST"])
def upload_images_to_cloudinary(request):
    if request.method == "POST":
        res = CloudinaryUpload(request.FILES['photos'], folder="/VelvetSocialMedia/")
        photo = TemporayImages(image_link=res['secure_url'])
        photo.save()
        return Response({"image": photo.image_link}, status=status.HTTP_201_CREATED)
    else:
        return Response({"message": "Method not allowed"})