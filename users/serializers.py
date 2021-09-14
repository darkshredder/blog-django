from __future__ import unicode_literals
from rest_framework import serializers
from users.models import Profile, Interest, BlogTag, Blog

class Interestserializer(serializers.ModelSerializer):

    class Meta:
        model = Interest
        fields = "__all__"

class ProfileSerializer(serializers.ModelSerializer):
    interests = Interestserializer(many=True, read_only=True)
    
    class Meta:
        model = Profile
        exclude = ('is_superuser', 'is_staff', 'is_active', 'user_permissions', 'groups')

class BlogTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogTag
        fields = "__all__"

class BlogSerializer(serializers.ModelSerializer):
    blog_tags = BlogTagSerializer(many=True, read_only=True)
    class Meta:
        model = Blog
        fields = "__all__"