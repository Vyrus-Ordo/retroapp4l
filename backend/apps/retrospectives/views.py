from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.retrospectives.models import (
	AccessLog,
	AccessLogAction,
	Milestone,
	Participant,
	Retrospective,
	RetrospectiveStatus,
)
from apps.retrospectives.serializers import (
	MilestoneSerializer,
	RetrospectiveCreateSerializer,
	RetrospectiveDetailSerializer,
	RetrospectiveListSerializer,
)


class RetrospectiveListCreateView(generics.ListCreateAPIView):
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		return (
			Retrospective.objects.filter(Q(facilitator=user) | Q(participants__user=user))
			.select_related("facilitator")
			.distinct()
		)

	def get_serializer_class(self):
		if self.request.method == "POST":
			return RetrospectiveCreateSerializer
		return RetrospectiveListSerializer

	def perform_create(self, serializer):
		retrospective = serializer.save(facilitator=self.request.user, status=RetrospectiveStatus.SETUP)
		Participant.objects.create(
			retrospective=retrospective,
			user=self.request.user,
			votes_remaining=retrospective.max_votes_per_user,
		)
		AccessLog.objects.create(
			retrospective=retrospective,
			action=AccessLogAction.OPENED,
			triggered_by=self.request.user,
			participant=self.request.user,
		)


class RetrospectiveDetailView(generics.RetrieveAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = RetrospectiveDetailSerializer

	def get_queryset(self):
		user = self.request.user
		return (
			Retrospective.objects.filter(Q(facilitator=user) | Q(participants__user=user))
			.select_related("facilitator")
			.prefetch_related("participants__user", "milestones")
			.distinct()
		)


class TeamSuggestionView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		query = request.query_params.get("q", "").strip()
		suggestions = Retrospective.objects.filter(facilitator=request.user)
		if query:
			suggestions = suggestions.filter(team_key__icontains=query)

		values = list(suggestions.values_list("team_key", flat=True).distinct().order_by("team_key"))
		return Response({"suggestions": values})

class MilestoneListCreateView(generics.ListCreateAPIView):
    serializer_class = MilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Milestone.objects.filter(retrospective_id=self.kwargs["retrospective_id"]).order_by("created_at")

    def perform_create(self, serializer):
        retrospective = Retrospective.objects.get(id=self.kwargs["retrospective_id"])
        if self.request.user != retrospective.facilitator:
            raise PermissionDenied("Only the facilitator can create milestones.")
        if retrospective.status != RetrospectiveStatus.SETUP:
            raise PermissionDenied("Milestones can only be created in setup phase.")
        serializer.save(author=self.request.user, retrospective=retrospective)

class MilestoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "milestone_id"

    def get_queryset(self):
        return Milestone.objects.filter(retrospective_id=self.kwargs["retrospective_id"]).order_by("created_at")

    def perform_update(self, serializer):
        milestone = self.get_object()
        retrospective = milestone.retrospective
        if self.request.user != retrospective.facilitator:
            raise PermissionDenied("Only the facilitator can edit milestones.")
        if retrospective.status != RetrospectiveStatus.SETUP:
            raise PermissionDenied("Milestones can only be edited in setup phase.")
        serializer.save()

    def perform_destroy(self, instance):
        retrospective = instance.retrospective
        if self.request.user != retrospective.facilitator:
            raise PermissionDenied("Only the facilitator can delete milestones.")
        if retrospective.status != RetrospectiveStatus.SETUP:
            raise PermissionDenied("Milestones can only be deleted in setup phase.")
        instance.delete()

# Create your views here.
