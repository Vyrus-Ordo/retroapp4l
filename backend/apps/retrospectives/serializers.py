from rest_framework import serializers

from apps.retrospectives.models import Milestone, Participant, Retrospective


class ParticipantSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Participant
        fields = ("id", "user", "user_name", "user_email", "votes_remaining", "joined_at")
        read_only_fields = fields


class MilestoneSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True)

    class Meta:
        model = Milestone
        fields = ("id", "category", "description", "author", "author_name", "created_at")
        read_only_fields = fields


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
            "skip_check_phase",
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
            "skip_check_phase",
            "timer_started_at",
            "timer_paused_at",
            "timer_duration_seconds",
            "created_at",
            "closed_at",
            "participants",
            "milestones",
        )
        read_only_fields = fields