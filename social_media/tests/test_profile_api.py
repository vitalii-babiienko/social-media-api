from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from social_media.models import Profile
from social_media.serializers import (
    ProfileListSerializer,
    ProfileDetailSerializer,
)

PROFILE_URL = reverse("social_media:profile-list")
NUMBER_OF_PROFILES = 10
PAGINATION_COUNT = 10


def create_users():
    return [
        get_user_model().objects.create_user(
            email=f"test{i}@test.com",
            password=f"test_pass{i}",
        )
        for i in range(NUMBER_OF_PROFILES)
    ]


def create_profiles(users):
    return [
        Profile.objects.create(
            user=users[i],
            username=f"test_user{i}",
            first_name=f"First Name {i}",
            last_name=f"Last Name {i}",
            bio=f"Bio {i}",
        )
        for i in range(NUMBER_OF_PROFILES)
    ]


def detail_url(profile_id):
    return reverse("social_media:profile-detail", args=[profile_id])


class UnauthenticatedProfileApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PROFILE_URL)

        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedProfileApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_pass",
        )
        self.client.force_authenticate(self.user)

    def test_list_profiles(self):
        users = create_users()
        create_profiles(users)

        res = self.client.get(PROFILE_URL)

        profiles = Profile.objects.order_by("id")
        serializer = ProfileListSerializer(profiles, many=True)

        self.assertEquals(res.status_code, status.HTTP_200_OK)

        for i in range(PAGINATION_COUNT):
            for key in serializer.data[i]:
                self.assertEquals(
                    res.data["results"][i][key],
                    serializer.data[i][key],
                )

    def test_retrieve_profile_detail(self):
        users = create_users()
        create_profiles(users)

        profile = Profile.objects.all()[0]

        url = detail_url(profile.id)
        res = self.client.get(url)

        serializer = ProfileDetailSerializer(profile)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, serializer.data)

    def test_follow_user(self):
        users = create_users()
        profile = create_profiles(users)[0]
        own_profile = Profile.objects.create(
            user=self.user,
            username="test_user",
        )

        res = self.client.post(
            reverse(
                "social_media:profile-follow-user",
                args=[profile.id],
            )
        )

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertIn(profile, own_profile.followings.all())

    def test_unfollow_user(self):
        users = create_users()
        profile = create_profiles(users)[0]
        own_profile = Profile.objects.create(
            user=self.user,
            username="test_user",
        )

        self.client.post(
            reverse(
                "social_media:profile-follow-user",
                args=[profile.id],
            )
        )

        res = self.client.post(
            reverse(
                "social_media:profile-unfollow-user",
                args=[profile.id],
            )
        )

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(profile, own_profile.followings.all())
