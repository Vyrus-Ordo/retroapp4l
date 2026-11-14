from django.urls import path

from apps.actions.review import (
    ActionsReviewDetailView,
    ActionsReviewListView,
    ActionsReviewTeamsView,
)
from apps.actions.views import (
    ActionItemDetailView,
    ActionItemListCreateView,
    PreviousActionListView,
    PreviousActionStatusUpdateView,
)

urlpatterns = [
    # Actions Review (spec docs/specs/ActionsReview/spec.md §3).
    # `actions/teams/` precisa vir ANTES de `actions/<uuid:action_id>/`.
    path("actions/", ActionsReviewListView.as_view(), name="actions-review-list"),
    path("actions/teams/", ActionsReviewTeamsView.as_view(), name="actions-review-teams"),
    path("actions/<uuid:action_id>/", ActionsReviewDetailView.as_view(), name="actions-review-detail"),
    path(
        "retrospectives/<uuid:retrospective_id>/action-items/",
        ActionItemListCreateView.as_view(),
        name="action-item-list-create",
    ),
    path(
        "retrospectives/<uuid:retrospective_id>/action-items/<uuid:action_id>/",
        ActionItemDetailView.as_view(),
        name="action-item-detail",
    ),
    path(
        "retrospectives/<uuid:retrospective_id>/previous-actions/",
        PreviousActionListView.as_view(),
        name="previous-actions-list",
    ),
    path(
        "retrospectives/<uuid:retrospective_id>/previous-actions/<uuid:action_id>/status/",
        PreviousActionStatusUpdateView.as_view(),
        name="previous-actions-status-update",
    ),
]