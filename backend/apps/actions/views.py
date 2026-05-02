from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.actions.models import ActionItem
from apps.actions.serializers import ActionItemSerializer, PreviousActionStatusSerializer
from apps.retrospectives.models import Participant, Retrospective, RetrospectiveStatus


class ActionAccessMixin:
	def get_retrospective(self):
		return Retrospective.objects.get(id=self.kwargs["retrospective_id"])

	def ensure_participant(self, retrospective, user):
		if not Participant.objects.filter(retrospective=retrospective, user=user).exists():
			raise PermissionDenied("Only participants can access action items in this retrospective.")

	def ensure_actions_phase(self, retrospective):
		if retrospective.status != RetrospectiveStatus.ACTIONS:
			raise PermissionDenied("Action items can only be modified during the actions phase.")

	def get_previous_closed_retrospective(self, retrospective):
		return (
			Retrospective.objects.filter(team_key=retrospective.team_key, status=RetrospectiveStatus.CLOSED)
			.exclude(id=retrospective.id)
			.filter(closed_at__isnull=False)
			.order_by("-closed_at", "-created_at")
			.first()
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
		self.ensure_actions_phase(retrospective)
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
		self.ensure_actions_phase(retrospective)
		serializer.save()

	def perform_destroy(self, instance):
		retrospective = self.get_retrospective_instance()
		self.ensure_participant(retrospective, self.request.user)
		self.ensure_actions_phase(retrospective)
		instance.delete()


class PreviousActionListView(ActionAccessMixin, APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, retrospective_id):
		retrospective = self.get_retrospective()
		self.ensure_participant(retrospective, request.user)
		previous_retrospective = self.get_previous_closed_retrospective(retrospective)
		if previous_retrospective is None:
			return Response({"retrospective_id": None, "action_items": []})

		serializer = ActionItemSerializer(
			ActionItem.objects.filter(retrospective=previous_retrospective).select_related("assignee", "card"),
			many=True,
			context={"request": request, "retrospective": previous_retrospective},
		)
		return Response(
			{
				"retrospective_id": str(previous_retrospective.id),
				"action_items": serializer.data,
			}
		)


class PreviousActionStatusUpdateView(ActionAccessMixin, APIView):
	permission_classes = [permissions.IsAuthenticated]

	def put(self, request, retrospective_id, action_id):
		retrospective = self.get_retrospective()
		self.ensure_participant(retrospective, request.user)

		previous_retrospective = self.get_previous_closed_retrospective(retrospective)
		if previous_retrospective is None:
			raise NotFound("No previous closed retrospective found for this team.")

		try:
			action_item = ActionItem.objects.get(id=action_id, retrospective=previous_retrospective)
		except ActionItem.DoesNotExist as error:
			raise NotFound("Action item not found in the previous retrospective.") from error

		serializer = PreviousActionStatusSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		action_item.status = serializer.validated_data["status"]
		action_item.save(update_fields=["status"])

		return Response(
			{
				"action_id": str(action_item.id),
				"status": action_item.status,
			},
			status=status.HTTP_200_OK,
		)
