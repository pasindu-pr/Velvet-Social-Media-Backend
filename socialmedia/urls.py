from xml.etree.ElementInclude import include
from django.db.models import base
from .views import CurrentUserProfile, FriendRequests, Friends, PostComments, PostLikes, PostPhotos, Posts, PostShares, RandomUsers, Timeline, upload_images_to_cloudinary
from django.urls import path 
from rest_framework_nested import routers

router = routers.DefaultRouter()

router.register('timeline', viewset=Timeline,basename='timeline')
router.register('posts', Posts, basename='Posts')
router.register('friends', Friends, basename='friends')
router.register('friends-requests', FriendRequests, basename='friends-requests')
router.register('random-users', RandomUsers, basename='random-users')

likes_router = routers.NestedDefaultRouter(router, parent_prefix='posts', lookup='post') 
likes_router.register('likes',PostLikes, basename='likes')

comments_router = routers.NestedDefaultRouter(router, parent_prefix='posts', lookup='post')
comments_router.register('comments', PostComments, basename='comments')

share_router = routers.NestedDefaultRouter(router, parent_prefix='posts', lookup='post')
share_router.register('shares', PostShares, basename='shares')

photos_router = routers.NestedDefaultRouter(router, parent_prefix='posts', lookup='post')
photos_router.register('photos', PostPhotos, basename='photos')

urlpatterns = [
     path("image_upload/", upload_images_to_cloudinary),
     path("current-profile/", CurrentUserProfile.as_view())
]  + router.urls + likes_router.urls + comments_router.urls + share_router.urls + photos_router.urls
