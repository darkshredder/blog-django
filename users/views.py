from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from users.serializers import ProfileSerializer, BlogSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Blog, BlogTag, Profile, Interest
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import status
from django.contrib.auth.models import update_last_login
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
import base64
from django.core.files.base import ContentFile
from django.conf import settings
from django.db.models import Q, Count
from collections import OrderedDict
from itertools import islice

class UserViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for Register or Login, Hobby Add,Delete and Fetch Profile users.
    """ 

    @action(detail=False, methods=['post'])
    def register(self, request):
        interests = request.data.pop('interests', None)
        profile = Profile.objects._create_user(
                **{**request.data,"username":request.data['username'],
                "full_name":request.data['full_name'],
                "password":request.data['password'],}
                
            )
        profile.set_password(request.data['password'])
        if interests:
            if len(interests) != 3:
                return Response({"message": "You should have three interests"}, status=status.HTTP_400_BAD_REQUEST)
            for interest in interests:
                interest = interest.lower().title()
                interestObject, created = Interest.objects.get_or_create(name=interest)
                profile.interests.add(interestObject)
                profile.save()
        
        serializer = ProfileSerializer(profile)

        return Response(serializer.data)



    @action(detail=False, methods=['post'])
    def login(self, request):
        
        data = request.data
        username = data.get("username", None)
        password = data.get("password", None)

        if not username:
            return Response("username should be provided ! ", status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response("Password cannot be empty", status=status.HTTP_400_BAD_REQUEST)
        try:
            profile = Profile.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response("username Not Found", status=status.HTTP_404_NOT_FOUND)

        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            update_last_login(None, user)

            return Response({"token": token.key}, status=status.HTTP_200_OK)

        return Response("Passwords does not match", status=status.HTTP_403_FORBIDDEN)
    


    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)


class BlogViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for Register or Login, Hobby Add,Delete and Fetch Profile users.
    """ 

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_new(self, request):
        tags = request.data.pop('tags', None)
        if len(tags)> 5:
            return Response({"message": "You should have max five tags"}, status=status.HTTP_400_BAD_REQUEST)
        
        blog_ser = BlogSerializer(data=request.data)
        if blog_ser.is_valid():
            
            blog = blog_ser.save(author=request.user)
            for tag in tags:
                val = tag.lower().title()
                tagObject, created = BlogTag.objects.get_or_create(tag=val)
                blog.blog_tags.add(tagObject)
                blog.save()        

        return Response(blog_ser.data)

from django.db.models import F
class FeedViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def top_feed(self, request):
        user = request.user
        user_interests = []
        for interest in user.interests.all():
            user_interests.append(interest.name)
    
        blogs = Blog.objects.filter(Q(blog_tags__tag__in=user_interests)).order_by('-pk')[:9]
        Blog.objects.filter(pk__in=blogs).update(impressions=F('impressions')+1)
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = Blog.objects.all()
        obj = get_object_or_404(queryset, pk=pk)
        Blog.objects.filter(pk__in=[pk]).update(impressions=F('impressions')+1)
        serializer = BlogSerializer(obj)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user_analytics(self, request):
        user = request.user
        user_interests = []
        for interest in user.interests.all():
            user_interests.append(interest.name)
        blogs = Blog.objects.filter(Q(author=user)).order_by('-impressions')[:4]
        Blog.objects.filter(pk__in=blogs).update(impressions=F('impressions')+1)
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def tag_percentage(self, request):
        tags = BlogTag.objects.all()
        res = {}
        for tag in tags:
            res[tag.tag] = tag.blog_tags.count()
        return Response(res)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def blog_city(self, request):
        blogs = Blog.objects.all()
        res = {}
        for blog in blogs:
            if blog.author.city in res:
                res[blog.author.city] += 1
            else:
                res[blog.author.city] = 1
        
        res = OrderedDict(sorted(res.items(), reverse=True))
        sliced = islice(res.items(), 5)  # o.iteritems() is o.items() in Python 3
        sliced_o = OrderedDict(sliced)
        return Response(sliced_o)
            