from django.db import transaction
from django.db.models import Count, F
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cards.models import Card, CardColumn, CardVote
from apps.cards.serializers import CardGroupingSerializer, CardSerializer, CardVoteSerializer, VotesConfigSerializer
from apps.retrospectives.models import Participant, Retrospective, RetrospectiveStatus


class RetrospectiveAccessMixin:
    def get_retrospective(self):
        return Retrospective.objects.get(id=self.kwargs["retrospective_id"])

    def get_cards_queryset(self):
        retrospective = self.get_retrospective()
        queryset = Card.objects.filter(retrospective_id=self.kwargs["retrospective_id"]).annotate(vote_count=Count("votes"))
        if retrospective.status == RetrospectiveStatus.DISCUSSION:
            return queryset.order_by("-vote_count", "created_at")
        return queryset.order_by("column", "position", "created_at")

    def ensure_participant(self, user):
        is_participant = Participant.objects.filter(
            retrospective_id=self.kwargs["retrospective_id"],
            user=user,
        ).exists()
        if not is_participant:
            raise PermissionDenied("Only participants can access cards in this retrospective.")

    def get_participant(self, retrospective, user):
        return Participant.objects.get(retrospective=retrospective, user=user)

    def ensure_facilitator(self, retrospective, user):
        if retrospective.facilitator != user:
            raise PermissionDenied("Only the facilitator can perform this action.")

    def ensure_voting_open(self, retrospective):
        if retrospective.status != RetrospectiveStatus.VOTING:
            raise PermissionDenied("Voting actions are only available during the voting phase.")

    def ensure_card_mutation_allowed(self, retrospective):
        if retrospective.status in {
            RetrospectiveStatus.DISCUSSION,
            RetrospectiveStatus.ACTIONS,
            RetrospectiveStatus.CLOSED,
        }:
            raise PermissionDenied("Cards are read-only during discussion, actions, and closed phases.")


class CardListCreateView(RetrospectiveAccessMixin, generics.ListCreateAPIView):
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.get_cards_queryset()

    def perform_create(self, serializer):
        retrospective = self.get_retrospective()
        self.ensure_participant(self.request.user)
        self.ensure_card_mutation_allowed(retrospective)

        serializer.save(author=self.request.user, retrospective_id=self.kwargs["retrospective_id"])  # author is always current user

    def create(self, request, *args, **kwargs):
        # Remove retrospective from validated_data if present
        data = request.data.copy()
        data.pop("retrospective", None)
        request._full_data = data
        return super().create(request, *args, **kwargs)

class CardDetailView(RetrospectiveAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "card_id"

    def get_queryset(self):
        return self.get_cards_queryset()

    def perform_update(self, serializer):
        retrospective = self.get_retrospective()
        card = self.get_object()
        if card.author != self.request.user:
            raise PermissionDenied("Only the author can edit this card.")
        self.ensure_card_mutation_allowed(retrospective)
        serializer.save()

    def update(self, request, *args, **kwargs):
        # Remove retrospective from validated_data if present
        data = request.data.copy()
        data.pop("retrospective", None)
        request._full_data = data
        return super().update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        retrospective = self.get_retrospective()
        if instance.author != self.request.user:
            raise PermissionDenied("Only the author can delete this card.")
        self.ensure_card_mutation_allowed(retrospective)
        instance.delete()


class CardGroupView(RetrospectiveAccessMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, retrospective_id):
        retrospective = self.get_retrospective()
        self.ensure_facilitator(retrospective, request.user)

        serializer = CardGroupingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        card_ids = serializer.validated_data["card_ids"]
        cards = list(Card.objects.filter(retrospective_id=retrospective_id, id__in=card_ids).order_by("created_at"))
        if len(cards) != len(card_ids):
            raise PermissionDenied("All selected cards must belong to this retrospective.")

        columns = {card.column for card in cards}
        if len(columns) != 1:
            raise PermissionDenied("Cards can only be grouped when they belong to the same column.")

        group_parent_id = serializer.validated_data.get("group_parent_id") or cards[0].id
        group_parent = next((card for card in cards if card.id == group_parent_id), None)
        if group_parent is None:
            raise PermissionDenied("The group parent card must be one of the selected cards.")

        with transaction.atomic():
            if group_parent.group_id is not None:
                group_parent.group = None
                group_parent.save(update_fields=["group"])

            grouped_card_ids = []
            for card in cards:
                if card.id == group_parent.id:
                    continue
                if card.group_id != group_parent.id:
                    card.group = group_parent
                    card.save(update_fields=["group"])
                grouped_card_ids.append(str(card.id))

        return Response(
            {
                "group_parent_id": str(group_parent.id),
                "card_ids": grouped_card_ids,
            },
            status=status.HTTP_200_OK,
        )


class CardUngroupView(RetrospectiveAccessMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, retrospective_id, card_id):
        retrospective = self.get_retrospective()
        self.ensure_facilitator(retrospective, request.user)

        card = Card.objects.get(retrospective_id=retrospective_id, id=card_id)
        previous_group_id = card.group_id
        card.group = None
        card.save(update_fields=["group"])

        return Response(
            {
                "card_id": str(card.id),
                "previous_group_id": str(previous_group_id) if previous_group_id else None,
            },
            status=status.HTTP_200_OK,
        )


class CardVoteView(RetrospectiveAccessMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, retrospective_id, card_id):
        retrospective = self.get_retrospective()
        self.ensure_voting_open(retrospective)
        participant = self.get_participant(retrospective, request.user)
        card = Card.objects.get(retrospective_id=retrospective_id, id=card_id)

        if card.column not in {CardColumn.LOATHED, CardColumn.LONGED}:
            raise PermissionDenied("Only cards in loathed or longed columns can be voted on.")
        if card.author_id == request.user.id:
            raise PermissionDenied("Users cannot vote on their own cards.")
        if participant.votes_remaining <= 0:
            raise PermissionDenied("No votes remaining for this participant.")

        with transaction.atomic():
            vote, created = CardVote.objects.get_or_create(card=card, voter=request.user)
            if not created:
                raise PermissionDenied("Only one vote per card is allowed for each participant.")

            participant.votes_remaining = F("votes_remaining") - 1
            participant.save(update_fields=["votes_remaining"])
            participant.refresh_from_db(fields=["votes_remaining"])

        return Response(
            {
                "card_id": str(card.id),
                "voter_id": str(request.user.id),
                "votes_remaining": participant.votes_remaining,
                "vote_id": str(vote.id),
            },
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, retrospective_id, card_id):
        retrospective = self.get_retrospective()
        self.ensure_voting_open(retrospective)
        participant = self.get_participant(retrospective, request.user)
        card = Card.objects.get(retrospective_id=retrospective_id, id=card_id)
        vote = CardVote.objects.get(card=card, voter=request.user)

        with transaction.atomic():
            participant.votes_remaining = F("votes_remaining") + 1
            participant.save(update_fields=["votes_remaining"])
            participant.refresh_from_db(fields=["votes_remaining"])
            vote.delete()

        return Response(
            {
                "card_id": str(card.id),
                "voter_id": str(request.user.id),
                "votes_remaining": participant.votes_remaining,
            },
            status=status.HTTP_200_OK,
        )


class VoteListView(RetrospectiveAccessMixin, generics.ListAPIView):
    serializer_class = CardVoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        self.ensure_participant(self.request.user)
        return CardVote.objects.filter(card__retrospective_id=self.kwargs["retrospective_id"]).order_by("created_at")


class VotesConfigView(RetrospectiveAccessMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, retrospective_id):
        retrospective = self.get_retrospective()
        self.ensure_facilitator(retrospective, request.user)
        if retrospective.status in {
            RetrospectiveStatus.VOTING,
            RetrospectiveStatus.DISCUSSION,
            RetrospectiveStatus.ACTIONS,
            RetrospectiveStatus.CLOSED,
        }:
            raise PermissionDenied("Votes configuration must be updated before the voting phase starts.")

        serializer = VotesConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        retrospective.max_votes_per_user = serializer.validated_data["max_votes_per_user"]
        retrospective.save(update_fields=["max_votes_per_user"])
        Participant.objects.filter(retrospective=retrospective).update(votes_remaining=retrospective.max_votes_per_user)

        return Response(
            {"max_votes_per_user": retrospective.max_votes_per_user},
            status=status.HTTP_200_OK,
        )
