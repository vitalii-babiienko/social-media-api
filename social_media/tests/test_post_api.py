from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from social_media.models import Profile, Post
from social_media.serializers import (
    PostListSerializer,
    PostDetailSerializer,
)

POST_LIST_URL = reverse("social_media:post-list")
NUMBER_OF_POSTS = 5
PAGINATION_COUNT = 5


def create_posts(author):
    return [
        Post.objects.create(
            author=author,
            title=f"Title {i}",
            content=f"Content {i}",
        )
        for i in range(NUMBER_OF_POSTS)
    ]


def detail_url(post_id):
    return reverse("social_media:post-detail", args=[post_id])


def like_unlike_url(post_id):
    return reverse("social_media:post-like-unlike-post", args=[post_id])


class UnauthenticatedPostApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(POST_LIST_URL)

        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPostApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_pass",
        )
        self.client.force_authenticate(self.user)
        self.profile = Profile.objects.create(
            user=self.user,
            username="test_user",
            first_name="First Name",
            last_name="Last Name",
            bio="Bio",
        )

    def test_list_posts(self):
        create_posts(self.profile)

        res = self.client.get(POST_LIST_URL)

        posts = Post.objects.order_by("-created_at")
        serializer = PostListSerializer(posts, many=True)

        self.assertEquals(res.status_code, status.HTTP_200_OK)

        for i in range(PAGINATION_COUNT):
            for key in serializer.data[i]:
                self.assertEquals(
                    res.data["results"][i][key],
                    serializer.data[i][key],
                )

    def test_retrieve_post_detail(self):
        create_posts(self.profile)

        post = Post.objects.all()[0]

        url = detail_url(post.id)
        res = self.client.get(url)

        serializer = PostDetailSerializer(post)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, serializer.data)

    def test_like_unlike_post(self):
        create_posts(self.profile)

        post = Post.objects.all()[0]

        url = like_unlike_url(post.id)
        res = self.client.post(url)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertIn(self.profile, post.likes.all())

        res = self.client.post(url)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.profile, post.likes.all())

    def test_add_comment(self):
        create_posts(self.profile)

        post = Post.objects.all()[0]

        payload = {
            "author": self.profile.id,
            "post": post.id,
            "content": "Test Content",
        }
        res = self.client.post(
            reverse("social_media:post-add-comment", args=[post.id]),
            payload,
        )

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(
            "{'detail': 'Your comment has been successfully added to the post.'}",
            str(res.data),
        )
