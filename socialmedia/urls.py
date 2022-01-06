from django.db.models import base
from .views import FriendRequests, Friends, PostComments, PostLikes, Posts, PostShares, Timeline
from django.urls import path 
from rest_framework_nested import routers

router = routers.DefaultRouter()

router.register('timeline', viewset=Timeline,basename='timeline')
router.register('posts', Posts, basename='Posts')
router.register('friends', Friends, basename='friends')
router.register('friends-requests', FriendRequests, basename='friends-requests')

likes_router = routers.NestedDefaultRouter(router, parent_prefix='posts', lookup='post') 
likes_router.register('likes',PostLikes, basename='likes')

comments_router = routers.NestedDefaultRouter(router, parent_prefix='posts', lookup='post')
comments_router.register('comments', PostComments, basename='comments')

share_router = routers.NestedDefaultRouter(router, parent_prefix='posts', lookup='post')
share_router.register('shares', PostShares, basename='shares')

urlpatterns = router.urls + likes_router.urls + comments_router.urls + share_router.urls
