"""Actions Review — visão persistente das ações dos times do usuário.

Implementa a spec `docs/specs/ActionsReview/spec.md` (seções 2, 3 e 7, parte de backend):

* `GET  /api/actions/`          — listagem paginada e filtrada das ações dos times legíveis
* `GET  /api/actions/teams/`    — times do usuário com contagens para o filtro
* `GET  /api/actions/{id}/`     — detalhe + `assignee_options`
* `PATCH /api/actions/{id}/`    — edição parcial (facilitador de time, retrospectiva fechada)

`POST`, `PUT` e `DELETE` não existem (405). Nenhuma mudança de schema.
"""

import uuid
from datetime import date

from django.db.models import Count, F, Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.actions.models import ActionItem, ActionItemStatus
from apps.actions.serializers import ActionItemSerializer
from apps.retrospectives.models import Participant, Retrospective, RetrospectiveStatus

PENDING_STATUSES = (ActionItemStatus.NOT_STARTED, ActionItemStatus.IN_PROGRESS)
VALID_STATUSES = {choice for choice, _label in ActionItemStatus.choices}
VALID_ORDERINGS = {
    "due_date",
    "-due_date",
    "status_updated_at",
    "-status_updated_at",
    "created_at",
    "-created_at",
}
DEFAULT_ORDERING = "due_date"


# ---------------------------------------------------------------------------
# Regras de acesso (spec §2)
# ---------------------------------------------------------------------------


def _reject_guest(user):
    """Convidados nunca acessam a Actions Review."""
    if user is None or not getattr(user, "is_authenticated", False):
        raise PermissionDenied("Authentication is required.")
    if user.is_guest:
        raise PermissionDenied("Guests cannot access the actions review.")


def readable_team_keys(user):
    """`team_key`s dos times onde o usuário é facilitador OU participante de ao menos uma retro."""
    _reject_guest(user)
    return set(
        Retrospective.objects.filter(Q(facilitator=user) | Q(participants__user=user))
        .values_list("team_key", flat=True)
        .distinct()
    )


def editable_team_keys(user):
    """`team_key`s dos times onde o usuário é facilitador de ao menos uma retro."""
    _reject_guest(user)
    return set(
        Retrospective.objects.filter(facilitator=user).values_list("team_key", flat=True)
    )


# ---------------------------------------------------------------------------
# Paginação (spec §3.1: padrão 25, máximo 100; o projeto não tem paginação global)
# ---------------------------------------------------------------------------


class ActionsReviewPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


# ---------------------------------------------------------------------------
# Filtros e ordenação (spec §3.1)
# ---------------------------------------------------------------------------


def _parse_date(params, name):
    raw = params.get(name)
    if raw in (None, ""):
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError as error:
        raise ValidationError({name: "Use the YYYY-MM-DD format."}) from error


def _apply_ordering(queryset, ordering):
    if ordering not in VALID_ORDERINGS:
        ordering = DEFAULT_ORDERING

    field = ordering.lstrip("-")
    expression = F(field)
    expression = expression.desc(nulls_last=True) if ordering.startswith("-") else expression.asc(nulls_last=True)

    # Desempate estável (spec §3.1): retro de origem, criação e id.
    return queryset.order_by(expression, "retrospective__closed_at", "created_at", "id")


def filter_review_actions(queryset, params, readable_keys, user):
    """Aplica os query params da spec §3.1 sobre um queryset já restrito aos times legíveis."""
    requested_team_keys = params.getlist("team_key")
    if requested_team_keys:
        allowed = [key for key in requested_team_keys if key in readable_keys]
        # Valor fora dos legíveis é ignorado (spec §3.1). Se nada legível sobra, o
        # filtro não restringe — a base já está limitada aos times do usuário.
        if allowed:
            queryset = queryset.filter(retrospective__team_key__in=allowed)

    requested_statuses = [item.strip() for item in params.getlist("status") if item.strip()]
    if requested_statuses:
        invalid = [item for item in requested_statuses if item not in VALID_STATUSES]
        if invalid:
            raise ValidationError({"status": f"Invalid status: {invalid[0]}."})
        queryset = queryset.filter(status__in=requested_statuses)

    assignee = params.get("assignee")
    if assignee:
        if assignee == "me":
            queryset = queryset.filter(assignee=user)
        else:
            try:
                assignee_id = uuid.UUID(assignee)
            except (ValueError, AttributeError, TypeError) as error:
                raise ValidationError({"assignee": "Invalid assignee."}) from error
            queryset = queryset.filter(assignee_id=assignee_id)

    overdue = (params.get("overdue") or "").lower()
    if overdue in {"true", "1", "yes"}:
        queryset = queryset.filter(due_date__lt=timezone.localdate()).exclude(status=ActionItemStatus.DONE)

    due_before = _parse_date(params, "due_before")
    if due_before is not None:
        queryset = queryset.filter(due_date__lte=due_before)

    due_after = _parse_date(params, "due_after")
    if due_after is not None:
        queryset = queryset.filter(due_date__gte=due_after)

    q = (params.get("q") or "").strip()
    if q:
        queryset = queryset.filter(description__icontains=q)

    return _apply_ordering(queryset, params.get("ordering") or DEFAULT_ORDERING)


def build_assignee_participant_map(actions):
    """`{(retrospective_id, user_id): participant_id}` para todos os itens da página — uma query."""
    retrospective_ids = {action.retrospective_id for action in actions}
    if not retrospective_ids:
        return {}
    rows = Participant.objects.filter(retrospective_id__in=retrospective_ids).values_list(
        "id", "retrospective_id", "user_id"
    )
    return {(retrospective_id, user_id): str(participant_id) for participant_id, retrospective_id, user_id in rows}


# ---------------------------------------------------------------------------
# Serializers de revisão (spec §3.1, §3.3)
# ---------------------------------------------------------------------------


class ReviewRetrospectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retrospective
        fields = ("id", "title", "sprint_name", "team_key", "status", "closed_at")
        read_only_fields = fields


class ActionReviewSerializer(serializers.ModelSerializer):
    """Item da listagem. Não expõe conteúdo nem autor do card (anonimato, spec §1)."""

    retrospective = ReviewRetrospectiveSerializer(read_only=True)
    is_overdue = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    assignee_name = serializers.CharField(source="assignee.name", read_only=True)
    assignee_user_id = serializers.UUIDField(source="assignee_id", read_only=True)
    # Emenda de 2026-11-14 (spec §3.1): permite ao frontend pré-selecionar o responsável
    # no modal de edição sem casar nomes (homônimos).
    assignee_participant_id = serializers.SerializerMethodField()

    class Meta:
        model = ActionItem
        fields = (
            "id",
            "description",
            "status",
            "status_updated_at",
            "due_date",
            "is_overdue",
            "external_tracker_url",
            "assignee_name",
            "assignee_user_id",
            "assignee_participant_id",
            "retrospective",
            "can_edit",
        )
        read_only_fields = fields

    def _editable_keys(self):
        return self.context.get("editable_team_keys", set())

    def get_is_overdue(self, obj):
        return bool(
            obj.due_date
            and obj.status != ActionItemStatus.DONE
            and obj.due_date < timezone.localdate()
        )

    def get_can_edit(self, obj):
        return bool(
            obj.retrospective.status == RetrospectiveStatus.CLOSED
            and obj.retrospective.team_key in self._editable_keys()
        )

    def get_assignee_participant_id(self, obj):
        mapping = self.context.get("assignee_participants")
        if mapping is not None:
            return mapping.get((obj.retrospective_id, obj.assignee_id))
        # Uso fora da listagem (ex.: detalhe isolado): uma query, nunca N+1.
        participant_id = (
            Participant.objects.filter(
                retrospective_id=obj.retrospective_id, user_id=obj.assignee_id
            )
            .values_list("id", flat=True)
            .first()
        )
        return str(participant_id) if participant_id else None


class ActionReviewDetailSerializer(ActionReviewSerializer):
    assignee_options = serializers.SerializerMethodField()

    class Meta(ActionReviewSerializer.Meta):
        fields = ActionReviewSerializer.Meta.fields + ("assignee_options",)
        read_only_fields = fields

    def get_assignee_options(self, obj):
        participants = obj.retrospective.participants.select_related("user").order_by("joined_at")
        return [
            {"participant_id": str(participant.id), "name": participant.user.name}
            for participant in participants
        ]


class ActionReviewUpdateSerializer(ActionItemSerializer):
    """PATCH parcial. Reaproveita `ActionItemSerializer.validate` (regra de `assignee_id`) sem duplicar.

    Campos aceitos são exatamente os da premissa D; `card`/`retrospective`/`id` são ignorados
    porque não fazem parte de `Meta.fields`.
    """

    class Meta(ActionItemSerializer.Meta):
        fields = ("description", "assignee_id", "due_date", "status", "external_tracker_url")
        read_only_fields = ("id", "status_updated_at")

    def validate_description(self, value):
        if value is None or not value.strip():
            raise serializers.ValidationError("This field may not be blank.")
        return value


# ---------------------------------------------------------------------------
# Views (spec §3)
# ---------------------------------------------------------------------------


class _ReviewAccessMixin:
    permission_classes = [IsAuthenticated]

    def readable_keys(self):
        if not hasattr(self, "_readable_keys"):
            self._readable_keys = readable_team_keys(self.request.user)
        return self._readable_keys

    def editable_keys(self):
        if not hasattr(self, "_editable_keys"):
            self._editable_keys = editable_team_keys(self.request.user)
        return self._editable_keys

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Calculado uma única vez por request: evita N+1 em `can_edit` e no responsável.
        context["editable_team_keys"] = self.editable_keys()
        context["assignee_participants"] = getattr(self, "_assignee_participants", None)
        return context


class ActionsReviewListView(_ReviewAccessMixin, ListAPIView):
    serializer_class = ActionReviewSerializer
    pagination_class = ActionsReviewPagination
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        readable = self.readable_keys()
        queryset = (
            ActionItem.objects.filter(retrospective__team_key__in=readable)
            .select_related("assignee", "retrospective")
            .distinct()
        )
        return filter_review_actions(queryset, self.request.query_params, readable, self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        actions = list(page) if page is not None else list(queryset)
        # Uma única query para resolver `assignee_participant_id` de toda a página.
        self._assignee_participants = build_assignee_participant_map(actions)
        serializer = self.get_serializer(actions, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class ActionsReviewTeamsView(_ReviewAccessMixin, APIView):
    http_method_names = ["get", "head", "options"]

    def get(self, request):
        readable = self.readable_keys()
        editable = self.editable_keys()
        rows = (
            Retrospective.objects.filter(team_key__in=readable)
            .values("team_key")
            .annotate(
                total=Count("action_items", distinct=True),
                pending=Count(
                    "action_items",
                    filter=Q(action_items__status__in=PENDING_STATUSES),
                    distinct=True,
                ),
            )
            .order_by("team_key")
        )
        return Response(
            [
                {
                    "team_key": row["team_key"],
                    "pending": row["pending"],
                    "total": row["total"],
                    "can_edit": row["team_key"] in editable,
                }
                for row in rows
            ]
        )


class ActionsReviewDetailView(_ReviewAccessMixin, RetrieveUpdateAPIView):
    lookup_url_kwarg = "action_id"
    http_method_names = ["get", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ActionReviewUpdateSerializer
        return ActionReviewDetailSerializer

    def get_queryset(self):
        # Time fora do alcance de leitura → 404 (não revela existência).
        return ActionItem.objects.filter(
            retrospective__team_key__in=self.readable_keys()
        ).select_related("assignee", "retrospective", "retrospective__facilitator")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        instance = getattr(self, "_instance", None)
        if self.request.method == "PATCH" and instance is not None:
            context["retrospective"] = instance.retrospective
        return context

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self._instance = instance
        retrospective = instance.retrospective

        if retrospective.team_key not in self.editable_keys():
            raise PermissionDenied("Only a facilitator of this team can edit its actions.")
        if retrospective.status != RetrospectiveStatus.CLOSED:
            raise PermissionDenied("Edit this action inside the retrospective")

        serializer = ActionReviewUpdateSerializer(
            instance,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        # save() sem `update_fields`: o `pre_save` mantém `status_updated_at`
        # e o `post_save` continua emitindo `action_updated`/`action_check_updated`.
        serializer.save()

        instance.refresh_from_db()
        return Response(ActionReviewDetailSerializer(instance, context=self.get_serializer_context()).data)
