from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from apps.cards.models import Card
from apps.cards.serializers import CardSerializer
from apps.retrospectives.models import Participant


class CardListCreateView(generics.ListCreateAPIView):
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Card.objects.filter(retrospective_id=self.kwargs["retrospective_id"]).order_by("column", "position", "created_at")

    def perform_create(self, serializer):
        is_participant = Participant.objects.filter(
            retrospective_id=self.kwargs["retrospective_id"],
            user=self.request.user,
        ).exists()
        if not is_participant:
            raise PermissionDenied("Only participants can create cards in this retrospective.")

        serializer.save(author=self.request.user, retrospective_id=self.kwargs["retrospective_id"])  # author is always current user

    def create(self, request, *args, **kwargs):
        # Remove retrospective from validated_data if present
        data = request.data.copy()
        data.pop("retrospective", None)
        request._full_data = data
        return super().create(request, *args, **kwargs)

class CardDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "card_id"

    def get_queryset(self):
        return Card.objects.filter(retrospective_id=self.kwargs["retrospective_id"]).order_by("column", "position", "created_at")

    def perform_update(self, serializer):
        card = self.get_object()
        if card.author != self.request.user:
            raise PermissionDenied("Only the author can edit this card.")
        serializer.save()

    def update(self, request, *args, **kwargs):
        # Remove retrospective from validated_data if present
        data = request.data.copy()
        data.pop("retrospective", None)
        request._full_data = data
        return super().update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Only the author can delete this card.")
        instance.delete()
