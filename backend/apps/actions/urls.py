from django.urls import path

from apps.actions.views import (
    ActionItemDetailView,
    ActionItemListCreateView,
    PreviousActionListView,
    PreviousActionStatusUpdateView,
)

urlpatterns = [
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