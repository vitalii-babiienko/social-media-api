import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


def create_custom_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)

    if hasattr(instance, "username"):
        new_name = instance.username
    else:
        new_name = instance.title

    return os.path.join(
        "uploads",
        f"{instance.__class__.__name__.lower()}s",
        f"{slugify(new_name)}-{uuid.uuid4()}{extension}"
    )


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    bio = models.TextField(max_length=2000, blank=True)
    followings = models.ManyToManyField(
        "self",
        related_name="followers",
        symmetrical=False,
        blank=True,
    )
    image = models.ImageField(
        upload_to=create_custom_image_file_path,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.username


class Hashtag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(max_length=25000)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    hashtags = models.ManyToManyField(
        Hashtag,
        related_name="posts",
        blank=True,
    )
    likes = models.ManyToManyField(
        Profile,
        related_name="posts_likes",
        blank=True,
    )
    image = models.ImageField(
        upload_to=create_custom_image_file_path,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Post '{self.title}' by {self.author}"


class Comment(models.Model):
    author = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author} created at {str(self.created_at)}"
