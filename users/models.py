from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import (AbstractUser)
from django.core.validators import RegexValidator
from users.customusermanager import CustomUserManager



class Interest(models.Model):

    name = models.CharField(max_length=50, verbose_name="Hobby name")
    
    def __str__(self):
        return self.name

    class Meta:
        """
        Meta class for Interest model
        """
        verbose_name_plural = 'Interests'



class AbstractProfile(AbstractUser):
    # remove useless model fields
    username = None
    first_name = None
    last_name = None
    email = None

    # indexed on tf_id and phone_number
    username = models.CharField(
        max_length=50, verbose_name="username", db_index=True, unique=True
    )

    full_name = models.CharField(max_length=50, verbose_name="full Name")
    interests = models.ManyToManyField(
        Interest, blank=True, related_name="interests")
    city = models.CharField(max_length=50, verbose_name="City")
    country = models.CharField(max_length=50, verbose_name="Country")
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.full_name


class Profile(AbstractProfile):
    class Meta:
        verbose_name_plural = "Profile"

class BlogTag(models.Model):
    tag = models.CharField(max_length=50, verbose_name="Tag")
    def __str__(self):
        return self.tag

    class Meta:
        verbose_name_plural = "Blog Tags"


class Blog(models.Model):
    title = models.CharField(max_length=50, verbose_name="Blog title", null=True, blank=True, default=None)
    body = models.TextField(verbose_name="Blog content", null=True, blank=True, default=None)
    author = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="blogs", null=True, blank=True, default=None)
    blog_tags = models.ManyToManyField(
        BlogTag, related_name="blog_tags", null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    impressions = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Blogs"
        unique_together = ('title', 'author')