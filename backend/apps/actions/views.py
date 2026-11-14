from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.actions.models import ActionItem, ActionItemStatus
from apps.actions.serializers import ActionItemSerializer, PreviousActionStatusSerializer
from apps.retrospectives.models import Participant, Retrospective, RetrospectiveStatus


class ActionAccessMixin:
	def get_retrospective(self):
		retrospective = Retrospective.objects.get(id=self.kwargs["retrospective_id"])
		self.ensure_session_open(retrospective)
		return retrospective

	def ensure_session_open(self, retrospective):
		if retrospective.status == RetrospectiveStatus.CLOSED:
			raise PermissionDenied("This retrospective is closed. Use the history endpoint instead.")

	def ensure_participant(self, retrospective, user):
		if not Participant.objects.filter(retrospective=retrospective, user=user).exists():
			raise PermissionDenied("Only participants can access action items in this retrospective.")

	def ensure_discussion_phase(self, retrospective):
		if retrospective.status != RetrospectiveStatus.DISCUSSION:
			raise PermissionDenied("Action items can only be created during the discussion phase.")

	def ensure_discussion_or_actions_phase(self, retrospective):
		if retrospective.status not in [RetrospectiveStatus.DISCUSSION, RetrospectiveStatus.ACTIONS]:
			raise PermissionDenied("Action items can only be modified during the discussion or actions phase.")

	def ensure_facilitator(self, retrospective, user):
		if retrospective.facilitator != user:
			raise PermissionDenied("Only the facilitator can perform this action.")

	def get_latest_closed_retrospective(self, retrospective):
		return (
			Retrospective.objects.filter(team_key=retrospective.team_key, status=RetrospectiveStatus.CLOSED)
			.exclude(id=retrospective.id)
			.filter(closed_at__isnull=False)
			.order_by("-closed_at", "-created_at")
			.first()
		)

	def get_pending_previous_actions(self, retrospective):
		return (
			ActionItem.objects.filter(
				retrospective__team_key=retrospective.team_key,
				retrospective__status=RetrospectiveStatus.CLOSED,
				status__in=[ActionItemStatus.NOT_STARTED, ActionItemStatus.IN_PROGRESS],
			)
			.exclude(retrospective=retrospective)
			.select_related("assignee", "card", "retrospective")
			.order_by("retrospective__closed_at", "created_at")
		)

	def get_recently_completed_actions(self, retrospective, latest_closed_retrospective):
		if latest_closed_retrospective is None or latest_closed_retrospective.closed_at is None:
			return ActionItem.objects.none()
		return (
			ActionItem.objects.filter(
				retrospective__team_key=retrospective.team_key,
				retrospective__status=RetrospectiveStatus.CLOSED,
				status=ActionItemStatus.DONE,
				status_updated_at__gt=latest_closed_retrospective.closed_at,
			)
			.exclude(retrospective=retrospective)
			.select_related("assignee", "card", "retrospective")
			.order_by("-status_updated_at")
		)


class ActionItemListCreateView(ActionAccessMixin, generics.ListCreateAPIView):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = ActionItemSerializer

	def get_retrospective_instance(self):
		if not hasattr(self, "_retrospective"):
			self._retrospective = self.get_retrospective()
		return self._retrospective

	def get_queryset(self):
		retrospective = self.get_retrospective_instance()
		self.ensure_participant(retrospective, self.request.user)
		return ActionItem.objects.filter(retrospective=retrospective).select_related("assignee", "card")

	def get_serializer_context(self):
		context = super().get_serializer_context()
		context["retrospective"] = self.get_retrospective_instance()
		return context

	def perform_create(self, serializer):
		retrospective = self.get_retrospective_instance()
		self.ensure_participant(retrospective, self.request.user)
		self.ensure_facilitator(retrospective, self.request.user)
		self.ensure_discussion_phase(retrospective)
		serializer.save(retrospective=retrospective)


class ActionItemDetailView(ActionAccessMixin, generics.RetrieveUpdateDestroyAPIView):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = ActionItemSerializer
	lookup_url_kwarg = "action_id"

	def get_retrospective_instance(self):
		if not hasattr(self, "_retrospective"):
			self._retrospective = self.get_retrospective()
		return self._retrospective

	def get_queryset(self):
		retrospective = self.get_retrospective_instance()
		self.ensure_participant(retrospective, self.request.user)
		return ActionItem.objects.filter(retrospective=retrospective).select_related("assignee", "card")

	def get_serializer_context(self):
		context = super().get_serializer_context()
		context["retrospective"] = self.get_retrospective_instance()
		return context

	def perform_update(self, serializer):
		retrospective = self.get_retrospective_instance()
		self.ensure_participant(retrospective, self.request.user)
		self.ensure_facilitator(retrospective, self.request.user)
		self.ensure_discussion_or_actions_phase(retrospective)
		serializer.save()

	def perform_destroy(self, instance):
		retrospective = self.get_retrospective_instance()
		self.ensure_participant(retrospective, self.request.user)
		self.ensure_facilitator(retrospective, self.request.user)
		self.ensure_discussion_or_actions_phase(retrospective)
		instance.delete()


class PreviousActionListView(ActionAccessMixin, APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, retrospective_id):
		retrospective = self.get_retrospective()
		self.ensure_participant(retrospective, request.user)

		latest_closed = self.get_latest_closed_retrospective(retrospective)
		context = {"request": request, "retrospective": retrospective}

		pending_serializer = ActionItemSerializer(
			self.get_pending_previous_actions(retrospective), many=True, context=context
		)
		completed_serializer = ActionItemSerializer(
			self.get_recently_completed_actions(retrospective, latest_closed), many=True, context=context
		)
		return Response(
			{
				"action_items": pending_serializer.data,
				"recently_completed": completed_serializer.data,
			}
		)


class PreviousActionStatusUpdateView(ActionAccessMixin, APIView):
	permission_classes = [permissions.IsAuthenticated]

	def put(self, request, retrospective_id, action_id):
		retrospective = self.get_retrospective()
		self.ensure_participant(retrospective, request.user)

		try:
			action_item = ActionItem.objects.select_related("retrospective").get(
				id=action_id,
				retrospective__team_key=retrospective.team_key,
				retrospective__status=RetrospectiveStatus.CLOSED,
			)
		except ActionItem.DoesNotExist as error:
			raise NotFound("Action item not found in a closed retrospective for this team.") from error

		serializer = PreviousActionStatusSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		action_item.status = serializer.validated_data["status"]
		action_item.save(update_fields=["status", "status_updated_at"])

		return Response(
			{
				"action_id": str(action_item.id),
				"status": action_item.status,
			},
			status=status.HTTP_200_OK,
		)
