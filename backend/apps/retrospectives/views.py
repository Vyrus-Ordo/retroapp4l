import uuid
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.actions.models import ActionItem
from apps.cards.models import Card, CardVote
from apps.retrospectives.models import (
	AccessLog,
	AccessLogAction,
	Milestone,
	Participant,
	Retrospective,
	RetrospectiveStatus,
)
from apps.retrospectives.serializers import (
	ClosedRetrospectiveDetailSerializer,
	InviteResolveSerializer,
	MilestoneSerializer,
	RetrospectiveCreateSerializer,
	RetrospectiveDetailSerializer,
	RetrospectiveHistorySerializer,
	RetrospectiveListSerializer,
)
from apps.users.serializers import GuestInviteJoinSerializer, UserSerializer

User = get_user_model()


def serialize_focus_card(card):
	return {
		"card_id": str(card.id),
		"author": card.author.name,
		"column": card.column,
		"content": card.content,
		"vote_count": card.vote_count,
	}


def ensure_invite_token(retrospective):
	if retrospective.status == RetrospectiveStatus.CLOSED or retrospective.invite_token:
		return False

	retrospective.invite_token = uuid.uuid4()
	retrospective.invite_revoked_at = None
	retrospective.save(update_fields=["invite_token", "invite_revoked_at"])
	return True


def get_invite_status(retrospective):
	now = timezone.now()
	if retrospective.status == RetrospectiveStatus.LOBBY and retrospective.invite_token:
		return "active", None
	if retrospective.invite_temporarily_open_until and retrospective.invite_temporarily_open_until > now:
		return "temporarily_open", retrospective.invite_temporarily_open_until
	return "blocked", None


def ensure_invite_open(retrospective):
	invite_status, _expires_at = get_invite_status(retrospective)
	if retrospective.status == RetrospectiveStatus.CLOSED:
		raise PermissionDenied("This retrospective is closed.")
	if invite_status == "blocked":
		raise PermissionDenied("Invite link is currently blocked.")
	return invite_status


def build_guest_identity(name, public_email=""):
	identifier = uuid.uuid4()
	return {
		"name": name,
		"email": f"guest+{identifier}@guest.retroapp4l.local",
		"public_email": public_email,
		"is_guest": True,
	}


class RetrospectiveAccessMixin:
	def get_accessible_queryset(self, user):
		return Retrospective.objects.filter(Q(facilitator=user) | Q(participants__user=user)).distinct()

	def get_retrospective(self):
		return self.get_accessible_queryset(self.request.user).get(id=self.kwargs["retrospective_id"])

	def ensure_session_open(self, retrospective):
		if retrospective.status == RetrospectiveStatus.CLOSED:
			raise PermissionDenied("This retrospective is closed. Use the history endpoint instead.")

	def ensure_facilitator(self, retrospective):
		if retrospective.facilitator != self.request.user:
			raise PermissionDenied("Only the facilitator can perform this action.")

	def ensure_participant(self, retrospective):
		if not Participant.objects.filter(retrospective=retrospective, user=self.request.user).exists():
			raise PermissionDenied("Only participants can access this retrospective.")

	def discussion_cards_queryset(self, retrospective):
		return Card.objects.filter(retrospective=retrospective).select_related("author").annotate(vote_count=Count("votes")).order_by("-vote_count", "created_at")

	def broadcast_phase_changed(self, retrospective):
		channel_layer = get_channel_layer()
		async_to_sync(channel_layer.group_send)(
			f"retro_{retrospective.id}",
			{
				"type": "phase_changed",
				"phase": retrospective.status,
				"timer_duration_seconds": retrospective.timer_duration_seconds or 0,
			},
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
		if getattr(self.request.user, "is_guest", False):
			raise PermissionDenied("Guest sessions cannot create retrospectives.")
		retrospective = serializer.save(facilitator=self.request.user, status=RetrospectiveStatus.SETUP)
		ensure_invite_token(retrospective)
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


class RetrospectiveDetailView(RetrospectiveAccessMixin, generics.RetrieveAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = RetrospectiveDetailSerializer

	def get_queryset(self):
		user = self.request.user
		return (
			Retrospective.objects.filter(Q(facilitator=user) | Q(participants__user=user))
			.select_related("facilitator", "focus_card")
			.prefetch_related("participants__user", "milestones")
			.distinct()
		)

	def get_object(self):
		retrospective = super().get_object()
		self.ensure_session_open(retrospective)
		ensure_invite_token(retrospective)
		return retrospective


class TeamSuggestionView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		if getattr(request.user, "is_guest", False):
			raise PermissionDenied("Guest sessions cannot access team suggestions.")
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
		if getattr(self.request.user, "is_guest", False):
			raise PermissionDenied("Guest sessions cannot create milestones.")
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
		if getattr(self.request.user, "is_guest", False):
			raise PermissionDenied("Guest sessions cannot edit milestones.")
		if self.request.user != retrospective.facilitator:
			raise PermissionDenied("Only the facilitator can edit milestones.")
		if retrospective.status != RetrospectiveStatus.SETUP:
			raise PermissionDenied("Milestones can only be edited in setup phase.")
		serializer.save()

	def perform_destroy(self, instance):
		retrospective = instance.retrospective
		if getattr(self.request.user, "is_guest", False):
			raise PermissionDenied("Guest sessions cannot delete milestones.")
		if self.request.user != retrospective.facilitator:
			raise PermissionDenied("Only the facilitator can delete milestones.")
		if retrospective.status != RetrospectiveStatus.SETUP:
			raise PermissionDenied("Milestones can only be deleted in setup phase.")
		instance.delete()


class InviteResolveView(APIView):
	permission_classes = [AllowAny]

	def get_retrospective(self, token):
		return Retrospective.objects.select_related("facilitator").get(invite_token=token)

	def get(self, request, token):
		retrospective = self.get_retrospective(token)
		serializer = InviteResolveSerializer(retrospective, context={"now": timezone.now()})
		return Response(serializer.data, status=status.HTTP_200_OK)


class InviteJoinView(APIView):
	permission_classes = [AllowAny]

	def get_retrospective(self, token):
		return Retrospective.objects.select_related("facilitator").get(invite_token=token)

	def get_or_create_join_user(self, request, serializer):
		if request.user.is_authenticated:
			user = request.user
			if getattr(user, "is_guest", False):
				updated_fields = []
				if user.name != serializer.validated_data["name"]:
					user.name = serializer.validated_data["name"]
					updated_fields.append("name")
				public_email = serializer.validated_data.get("email", "")
				if user.public_email != public_email:
					user.public_email = public_email
					updated_fields.append("public_email")
				if updated_fields:
					user.save(update_fields=updated_fields)
			return user

		identity = build_guest_identity(
			name=serializer.validated_data["name"],
			public_email=serializer.validated_data.get("email", ""),
		)
		user = User.objects.create_user(**identity)
		user.set_unusable_password()
		user.save(update_fields=["password"])
		return user

	def post(self, request, token):
		retrospective = self.get_retrospective(token)
		ensure_invite_open(retrospective)
		serializer = GuestInviteJoinSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		user = self.get_or_create_join_user(request, serializer)
		participant, created = Participant.objects.get_or_create(
			retrospective=retrospective,
			user=user,
			defaults={"votes_remaining": retrospective.max_votes_per_user},
		)
		if not created and participant.votes_remaining <= 0:
			participant.votes_remaining = retrospective.max_votes_per_user
			participant.save(update_fields=["votes_remaining"])

		if created:
			AccessLog.objects.create(
				retrospective=retrospective,
				action=AccessLogAction.PARTICIPANT_JOINED,
				triggered_by=None if getattr(user, "is_guest", False) else user,
				participant=user,
			)

		refresh = RefreshToken.for_user(user)
		return Response(
			{
				"user": UserSerializer(user).data,
				"access": str(refresh.access_token),
				"refresh": str(refresh),
				"retrospective_id": str(retrospective.id),
				"participant_id": str(participant.id),
			},
			status=status.HTTP_200_OK,
		)


class RetrospectiveHistoryView(RetrospectiveAccessMixin, generics.ListAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = RetrospectiveHistorySerializer

	def get_queryset(self):
		return (
			self.get_accessible_queryset(self.request.user)
			.filter(status=RetrospectiveStatus.CLOSED)
			.annotate(cards_count=Count("cards", distinct=True), action_items_count=Count("action_items", distinct=True))
			.prefetch_related("action_items")
			.order_by("-closed_at", "-created_at")
		)


class ClosedRetrospectiveDetailView(RetrospectiveAccessMixin, generics.RetrieveAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = ClosedRetrospectiveDetailSerializer
	lookup_url_kwarg = "retrospective_id"

	def get_queryset(self):
		return (
			self.get_accessible_queryset(self.request.user)
			.filter(status=RetrospectiveStatus.CLOSED)
			.prefetch_related(
				"participants__user",
				"milestones",
				Prefetch("cards", queryset=Card.objects.select_related("author").annotate(vote_count=Count("votes")).order_by("-vote_count", "created_at")),
				Prefetch("action_items", queryset=ActionItem.objects.select_related("assignee", "card")),
			)
			.select_related("facilitator", "focus_card")
		)

	def get_object(self):
		retrospective = super().get_object()
		retrospective.all_votes = CardVote.objects.filter(card__retrospective=retrospective).order_by("created_at")
		return retrospective


class RetrospectiveCloseView(RetrospectiveAccessMixin, APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, retrospective_id):
		retrospective = self.get_retrospective()
		self.ensure_facilitator(retrospective)
		if retrospective.status != RetrospectiveStatus.ACTIONS:
			raise PermissionDenied("Retrospectives can only be closed during the actions phase.")
		if request.data.get("confirm") is not True:
			return Response({"confirm": ["This field must be true to close the retrospective."]}, status=status.HTTP_400_BAD_REQUEST)

		now = timezone.now()
		retrospective.status = RetrospectiveStatus.CLOSED
		retrospective.closed_at = now
		retrospective.invite_token = None
		retrospective.invite_revoked_at = now
		retrospective.focus_card = None
		retrospective.save(update_fields=["status", "closed_at", "invite_token", "invite_revoked_at", "focus_card"])

		AccessLog.objects.create(
			retrospective=retrospective,
			action=AccessLogAction.CLOSED,
			triggered_by=request.user,
			participant=request.user,
		)
		self.broadcast_phase_changed(retrospective)

		return Response(
			{
				"id": str(retrospective.id),
				"status": retrospective.status,
				"closed_at": retrospective.closed_at,
			},
			status=status.HTTP_200_OK,
		)


class RetrospectiveFocusCardView(RetrospectiveAccessMixin, APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, retrospective_id):
		retrospective = self.get_retrospective()
		self.ensure_facilitator(retrospective)
		if retrospective.status != RetrospectiveStatus.DISCUSSION:
			raise PermissionDenied("Focus card can only be updated during the discussion phase.")

		card_id = request.data.get("card_id")
		if not card_id:
			return Response({"card_id": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

		try:
			card = self.discussion_cards_queryset(retrospective).get(id=card_id)
		except Card.DoesNotExist as error:
			raise PermissionDenied("Card must belong to this retrospective.") from error

		retrospective.focus_card_id = card.id
		retrospective.save(update_fields=["focus_card"])

		channel_layer = get_channel_layer()
		async_to_sync(channel_layer.group_send)(
			f"retro_{retrospective.id}",
			{
				"type": "discussion_focus_updated",
				**serialize_focus_card(card),
			},
		)

		return Response(serialize_focus_card(card), status=status.HTTP_200_OK)


class RetrospectiveNextFocusCardView(RetrospectiveAccessMixin, APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, retrospective_id):
		retrospective = self.get_retrospective()
		self.ensure_facilitator(retrospective)
		if retrospective.status != RetrospectiveStatus.DISCUSSION:
			raise PermissionDenied("Focus card can only be updated during the discussion phase.")

		cards = list(self.discussion_cards_queryset(retrospective))
		if not cards:
			return Response({"detail": "No cards available for discussion."}, status=status.HTTP_400_BAD_REQUEST)

		if retrospective.focus_card_id is None:
			next_card = cards[0]
		else:
			current_index = next((index for index, card in enumerate(cards) if card.id == retrospective.focus_card_id), None)
			if current_index is None or current_index + 1 >= len(cards):
				next_card = cards[0]
			else:
				next_card = cards[current_index + 1]

		retrospective.focus_card = next_card
		retrospective.save(update_fields=["focus_card"])

		channel_layer = get_channel_layer()
		async_to_sync(channel_layer.group_send)(
			f"retro_{retrospective.id}",
			{
				"type": "discussion_focus_updated",
				**serialize_focus_card(next_card),
			},
		)

		return Response(serialize_focus_card(next_card), status=status.HTTP_200_OK)


class ReopenEntryView(RetrospectiveAccessMixin, APIView):
	"""POST /api/retrospectives/{id}/reopen-entry/ — Facilitador reabre link por 2 minutos."""

	permission_classes = [IsAuthenticated]

	REOPEN_DURATION_SECONDS = 120

	def post(self, request, retrospective_id):
		retrospective = self.get_retrospective()
		self.ensure_facilitator(retrospective)

		if retrospective.status == RetrospectiveStatus.LOBBY:
			return Response(
				{"detail": "Invite link is already open during lobby phase."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		if retrospective.status == RetrospectiveStatus.CLOSED:
			return Response(
				{"detail": "Cannot reopen entry for a closed retrospective."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		now = timezone.now()
		retrospective.invite_temporarily_open_until = now + timedelta(seconds=self.REOPEN_DURATION_SECONDS)
		retrospective.save(update_fields=["invite_temporarily_open_until"])

		AccessLog.objects.create(
			retrospective=retrospective,
			action=AccessLogAction.LINK_REOPENED,
			triggered_by=request.user,
		)

		# Broadcast invite status update to all participants
		channel_layer = get_channel_layer()
		async_to_sync(channel_layer.group_send)(
			f"retro_{retrospective.id}",
			{
				"type": "invite_status_updated",
				"invite_status": "temporarily_open",
				"expires_at": retrospective.invite_temporarily_open_until.isoformat(),
			},
		)

		# Schedule auto-block task
		from tasks.invite import auto_block_invite
		auto_block_invite.apply_async(
			args=[str(retrospective.id)],
			countdown=self.REOPEN_DURATION_SECONDS,
		)

		return Response(
			{
				"status": "temporarily_open",
				"expires_at": retrospective.invite_temporarily_open_until.isoformat(),
			},
			status=status.HTTP_200_OK,
		)


class InviteStatusView(RetrospectiveAccessMixin, APIView):
	"""GET /api/retrospectives/{id}/invite-status/ — Status atual do link de convite."""

	permission_classes = [IsAuthenticated]

	def get(self, request, retrospective_id):
		retrospective = self.get_retrospective()
		now = timezone.now()

		if retrospective.status == RetrospectiveStatus.LOBBY and retrospective.invite_token:
			invite_status = "active"
			expires_at = None
		elif (
			retrospective.invite_temporarily_open_until
			and retrospective.invite_temporarily_open_until > now
		):
			invite_status = "temporarily_open"
			expires_at = retrospective.invite_temporarily_open_until.isoformat()
		else:
			invite_status = "blocked"
			expires_at = None

		return Response(
			{"status": invite_status, "expires_at": expires_at},
			status=status.HTTP_200_OK,
		)


class PresenceView(RetrospectiveAccessMixin, APIView):
	"""GET /api/retrospectives/{id}/presence/ — Lista participantes online."""

	permission_classes = [IsAuthenticated]

	def get(self, request, retrospective_id):
		retrospective = self.get_retrospective()
		self.ensure_session_open(retrospective)
		participants = (
			Participant.objects.filter(retrospective=retrospective)
			.select_related("user")
			.order_by("joined_at")
		)
		data = [
			{
				"user_id": str(p.user_id),
				"name": p.user.name,
				"avatar_url": p.user.avatar_url if hasattr(p.user, "avatar_url") else None,
				"joined_at": p.joined_at.isoformat(),
			}
			for p in participants
		]
		return Response({"participants": data}, status=status.HTTP_200_OK)

# Create your views here.
