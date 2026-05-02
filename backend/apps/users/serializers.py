from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ("id", "name", "email", "avatar_url", "oauth_provider", "created_at", "is_guest")
        read_only_fields = fields

    def get_email(self, obj):
        return obj.display_email


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "name", "email", "password")
        read_only_fields = ("id",)

    def validate_email(self, value: str) -> str:
        allowed_domains = getattr(settings, "ALLOWED_EMAIL_DOMAINS", [])
        if not allowed_domains:
            return value

        domain = value.rsplit("@", 1)[-1].lower()
        allowed = {item.lower() for item in allowed_domains}
        if domain not in allowed:
            raise serializers.ValidationError("Email domain is not allowed.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class GuestInviteJoinSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate_name(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("This field is required.")
        return value