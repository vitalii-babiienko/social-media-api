from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import (
    Profile,
    Hashtag,
    Post,
)
from social_media.paginations import (
    ProfilePagination,
    HashtagPagination,
    PostPagination,
)
from social_media.permissions import (
    IsProfileOwnerOrReadOnly,
    IsPostOwnerOrReadOnly,
)
from social_media.serializers import (
    ProfileSerializer,
    ProfileListSerializer,
    ProfileDetailSerializer,
    ProfileImageSerializer,
    HashtagSerializer,
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostImageSerializer,
    CommentAddSerializer,
)


class UploadImageMixin:
    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading the image to the specific instance"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileViewSet(UploadImageMixin, viewsets.ModelViewSet):
    queryset = (
        Profile.objects
        .select_related("user")
        .prefetch_related(
            "followings",
            "followers",
        )
        .annotate(followers_count=Count("followers"))
        .order_by("username")
    )
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, IsProfileOwnerOrReadOnly)
    pagination_class = ProfilePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        "username",
        "first_name",
        "last_name",
    )

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer

        if self.action == "retrieve":
            return ProfileDetailSerializer

        if self.action == "upload_image":
            return ProfileImageSerializer

        return ProfileSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="follow",
        permission_classes=[IsAuthenticated],
    )
    def follow_user(self, request, pk=None):
        """Endpoint for subscribing to a user"""
        profile = self.get_object()
        own_profile = self.request.user.profile

        if (
            profile != own_profile
            and own_profile not in profile.followers.all()
        ):
            profile.followers.add(own_profile)
            return Response(
                {"detail": f"You have successfully followed {profile}."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": f"You have already followed {profile}!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="unfollow",
        permission_classes=[IsAuthenticated],
    )
    def unfollow_user(self, request, pk=None):
        """Endpoint for unsubscribing to a user"""
        profile = self.get_object()
        own_profile = self.request.user.profile

        if (
            profile != own_profile
            and own_profile in profile.followers.all()
        ):
            profile.followers.remove(own_profile)
            return Response(
                {"detail": f"You have successfully unfollowed {profile}."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": f"You have not followed {profile} yet!"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = HashtagPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("name",)


class PostViewSet(UploadImageMixin, viewsets.ModelViewSet):
    queryset = (
        Post.objects
        .select_related("author")
        .prefetch_related(
            "hashtags",
            "comments__author",
        )
        .annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
        )
        .order_by("-created_at")
    )
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsPostOwnerOrReadOnly)
    pagination_class = PostPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        "title",
        "created_at",
        "author",
        "hashtags",
    )

    def get_serializer_class(self):
        if self.action in (
            "list",
            "show_favorite_posts",
            "show_posts_from_subscriptions_only",
        ):
            return PostListSerializer

        if self.action == "retrieve":
            return PostDetailSerializer

        if self.action == "upload_image":
            return PostImageSerializer

        if self.action == "add_comment":
            return CommentAddSerializer

        return PostSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="like-unlike",
        permission_classes=[IsAuthenticated],
    )
    def like_unlike_post(self, request, pk=None):
        """Endpoint for liking/unliking posts feature"""
        post = self.get_object()
        own_profile = self.request.user.profile

        if own_profile not in post.likes.all():
            post.likes.add(own_profile)
            return Response(
                {"detail": "You have successfully liked the post."},
                status=status.HTTP_200_OK,
            )

        post.likes.remove(own_profile)
        return Response(
            {"detail": "Your like was successfully removed."},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["GET"],
        detail=False,
        url_path="favorite",
        permission_classes=[IsAuthenticated],
    )
    def show_favorite_posts(self, request):
        """Endpoint for showing a list of the favorite posts"""
        own_profile = self.request.user.profile
        posts = Post.objects.filter(likes=own_profile)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="add-comment",
        permission_classes=[IsAuthenticated],
    )
    def add_comment(self, request, pk=None):
        """Endpoint for adding a comment to the post"""
        own_profile = self.request.user.profile
        post = self.get_object()
        serializer = CommentAddSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(
            author=own_profile,
            post=post,
            content=serializer.validated_data["content"],
        )
        return Response(
            {
                "detail": "Your comment has been successfully "
                          "added to the post."
            },
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["GET"],
        detail=False,
        url_path="subscriptions-only",
        permission_classes=[IsAuthenticated],
    )
    def show_posts_from_subscriptions_only(self, request):
        """Endpoint for showing a list of the posts from subscriptions only"""
        own_profile = self.request.user.profile
        posts = Post.objects.filter(author__in=own_profile.followings.all())
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
