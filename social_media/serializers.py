from rest_framework import serializers

from social_media.models import (
    Profile,
    Hashtag,
    Post,
    Comment,
)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "bio",
        )


class ProfileListSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "followers_count",
            "image",
        )


class ProfileDetailSerializer(serializers.ModelSerializer):
    followings = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="username",
    )
    followers = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="username",
    )

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "bio",
            "followings",
            "followers",
            "image",
        )


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "image")


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("id", "name")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "post",
            "content",
            "created_at",
        )


class CommentDetailSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="username",
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "content",
            "created_at",
        )


class CommentAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "content")


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "created_at",
            "hashtags",
        )


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="username",
    )
    hashtags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "content",
            "created_at",
            "hashtags",
            "likes_count",
            "comments_count",
            "image",
        )


class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="username",
    )
    hashtags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )
    likes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="username",
    )
    comments = CommentDetailSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "content",
            "created_at",
            "hashtags",
            "likes",
            "comments",
            "image",
        )


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "image")
