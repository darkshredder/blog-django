from __future__ import unicode_literals
from users.views import BlogViewSet, FeedViewSet, UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'auth/users', UserViewSet, basename='user')
router.register(r'blogs', BlogViewSet, basename='user')
router.register(r'feeds', FeedViewSet, basename='user')

urlpatterns = router.urls