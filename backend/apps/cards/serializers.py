from rest_framework import serializers

from apps.cards.models import Card, CardVote


class CardSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    author_display = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    group_parent_id = serializers.UUIDField(source="group_id", read_only=True)
    vote_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Card
        fields = (
            "id",
            "retrospective",
            "author",
            "author_name",
            "author_display",
            "column",
            "content",
            "is_anonymous",
            "group",
            "group_parent_id",
            "position",
            "vote_count",
            "can_edit",
            "created_at",
        )
        read_only_fields = ("id", "author", "author_name", "author_display", "can_edit", "created_at", "retrospective")

    def get_author(self, obj):
        if obj.is_anonymous:
            return None
        return str(obj.author_id)

    def get_author_name(self, obj):
        if obj.is_anonymous:
            return None
        return obj.author.name

    def get_author_display(self, obj):
        if obj.is_anonymous:
            return "Anonymous"
        return obj.author.name

    def get_can_edit(self, obj):
        request = self.context.get("request")
        if request is None or not request.user or not request.user.is_authenticated:
            return False
        return obj.author_id == request.user.id

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
