from rest_framework import serializers

from apps.actions.models import ActionItem, ActionItemStatus
from apps.cards.models import Card
from apps.retrospectives.models import Participant


class ActionItemSerializer(serializers.ModelSerializer):
    assignee_id = serializers.UUIDField(write_only=True, required=False)
    assignee_name = serializers.CharField(source="assignee.name", read_only=True)
    card_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    participant_id = serializers.SerializerMethodField()
    card = serializers.UUIDField(source="card_id", read_only=True)

    class Meta:
        model = ActionItem
        fields = (
            "id",
            "retrospective",
            "card",
            "card_id",
            "description",
            "assignee",
            "assignee_id",
            "assignee_name",
            "participant_id",
            "due_date",
            "status",
            "external_tracker_url",
            "created_at",
        )
        read_only_fields = (
            "id",
            "retrospective",
            "assignee",
            "assignee_name",
            "participant_id",
            "card",
            "created_at",
        )

    def get_participant_id(self, obj):
        participant = Participant.objects.filter(
            retrospective=obj.retrospective,
            user=obj.assignee,
        ).values_list("id", flat=True).first()
        return str(participant) if participant else None

    def validate(self, attrs):
        retrospective = self.context["retrospective"]
        assignee_id = attrs.pop("assignee_id", None)
        card_id = attrs.pop("card_id", serializers.empty)

        if self.instance is None and assignee_id is None:
            raise serializers.ValidationError({"assignee_id": "This field is required."})

        if assignee_id is not None:
            try:
                participant = Participant.objects.select_related("user").get(
                    id=assignee_id,
                    retrospective=retrospective,
                )
            except Participant.DoesNotExist as error:
                raise serializers.ValidationError({"assignee_id": "Assignee must be a participant in this retrospective."}) from error
            attrs["assignee"] = participant.user

        if card_id is not serializers.empty:
            if card_id is None:
                attrs["card"] = None
            else:
                try:
                    attrs["card"] = Card.objects.get(id=card_id, retrospective=retrospective)
                except Card.DoesNotExist as error:
                    raise serializers.ValidationError({"card_id": "Card must belong to this retrospective."}) from error

        return attrs


class PreviousActionStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=(
            ActionItemStatus.NOT_STARTED,
            ActionItemStatus.IN_PROGRESS,
            ActionItemStatus.DONE,
            "pending",
        )
    )

    def validate_status(self, value):
        if value == "pending":
            return ActionItemStatus.NOT_STARTED
        return value