from rest_framework import serializers

from apps.cards.models import Card


class CardSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True)

    class Meta:
        model = Card
        fields = (
            "id",
            "retrospective",
            "author",
            "author_name",
            "column",
            "content",
            "group",
            "position",
            "created_at",
        )
        read_only_fields = ("id", "author", "author_name", "created_at", "retrospective")

    def validate_content(self, value):
        if len(value) > 500:
            raise serializers.ValidationError("Card content must be 500 characters or less.")
        return value
