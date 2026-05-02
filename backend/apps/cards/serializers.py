from rest_framework import serializers

from apps.cards.models import Card, CardVote


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


class CardGroupingSerializer(serializers.Serializer):
    card_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        min_length=2,
    )
    group_parent_id = serializers.UUIDField(required=False, allow_null=True)


class CardVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardVote
        fields = ("id", "card", "voter", "created_at")
        read_only_fields = fields


class VotesConfigSerializer(serializers.Serializer):
    max_votes_per_user = serializers.IntegerField(min_value=1, max_value=10)
