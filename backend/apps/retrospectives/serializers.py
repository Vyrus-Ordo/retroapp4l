from rest_framework import serializers

from apps.actions.serializers import ActionItemSerializer
from apps.cards.serializers import CardSerializer, CardVoteSerializer
from apps.retrospectives.models import Milestone, Participant, Retrospective


class ParticipantSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = ("id", "user", "user_name", "user_email", "votes_remaining", "joined_at")
        read_only_fields = fields

    def get_user_email(self, obj):
        return obj.user.display_email


class InviteResolveSerializer(serializers.ModelSerializer):
    facilitator_name = serializers.CharField(source="facilitator.name", read_only=True)
    invite_status = serializers.SerializerMethodField()
    entry_expires_at = serializers.SerializerMethodField()

    class Meta:
        model = Retrospective
        fields = (
            "id",
            "title",
            "sprint_name",
            "team_key",
            "status",
            "facilitator_name",
            "invite_status",
            "entry_expires_at",
        )
        read_only_fields = fields

    def get_invite_status(self, obj):
        now = self.context["now"]
        if obj.status == "lobby" and obj.invite_token:
            return "active"
        if obj.invite_temporarily_open_until and obj.invite_temporarily_open_until > now:
            return "temporarily_open"
        return "blocked"

    def get_entry_expires_at(self, obj):
        now = self.context["now"]
        if obj.invite_temporarily_open_until and obj.invite_temporarily_open_until > now:
            return obj.invite_temporarily_open_until
        return None


class MilestoneSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True)

    class Meta:
        model = Milestone
        fields = ("id", "category", "description", "author", "author_name", "created_at")
        read_only_fields = ("id", "author", "author_name", "created_at")


class RetrospectiveCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retrospective
        fields = (
            "id",
            "title",
            "sprint_name",
            "description",
            "team_key",
            "max_votes_per_user",
            "allow_self_vote",
            "skip_check_phase",
            "phase_durations",
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "team_key": {"required": True},
        }


class RetrospectiveListSerializer(serializers.ModelSerializer):
    facilitator_name = serializers.CharField(source="facilitator.name", read_only=True)

    class Meta:
        model = Retrospective
        fields = (
            "id",
            "title",
            "sprint_name",
            "team_key",
            "status",
            "facilitator",
            "facilitator_name",
            "created_at",
        )
        read_only_fields = fields


class RetrospectiveDetailSerializer(serializers.ModelSerializer):
    facilitator_name = serializers.CharField(source="facilitator.name", read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)
    milestones = MilestoneSerializer(many=True, read_only=True)
    focus_card_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Retrospective
        fields = (
            "id",
            "title",
            "sprint_name",
            "description",
            "team_key",
            "status",
            "facilitator",
            "facilitator_name",
            "invite_token",
            "invite_revoked_at",
            "max_votes_per_user",
            "allow_self_vote",
            "skip_check_phase",
            "focus_card_id",
            "timer_started_at",
            "timer_paused_at",
            "timer_duration_seconds",
            "phase_durations",
            "created_at",
            "closed_at",
            "participants",
            "milestones",
        )
        read_only_fields = fields


class RetrospectiveHistorySerializer(serializers.ModelSerializer):
    cards_count = serializers.IntegerField(read_only=True)
    action_items_count = serializers.IntegerField(read_only=True)
    action_item_status_summary = serializers.SerializerMethodField()

    class Meta:
        model = Retrospective
        fields = (
            "id",
            "title",
            "sprint_name",
            "team_key",
            "closed_at",
            "cards_count",
            "action_items_count",
            "action_item_status_summary",
        )
        read_only_fields = fields

    def get_action_item_status_summary(self, obj):
        summary = {"not_started": 0, "in_progress": 0, "done": 0}
        for status_value in obj.action_items.values_list("status", flat=True):
            if status_value in summary:
                summary[status_value] += 1
        return summary


class ClosedRetrospectiveDetailSerializer(serializers.ModelSerializer):
    facilitator_name = serializers.CharField(source="facilitator.name", read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)
    milestones = MilestoneSerializer(many=True, read_only=True)
    cards = CardSerializer(many=True, read_only=True)
    votes = CardVoteSerializer(source="all_votes", many=True, read_only=True)
    action_items = ActionItemSerializer(many=True, read_only=True)
    focus_card_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Retrospective
        fields = (
            "id",
            "title",
            "sprint_name",
            "description",
            "team_key",
            "status",
            "facilitator",
            "facilitator_name",
            "closed_at",
            "focus_card_id",
            "participants",
            "milestones",
            "cards",
            "votes",
            "action_items",
        )
        read_only_fields = fields