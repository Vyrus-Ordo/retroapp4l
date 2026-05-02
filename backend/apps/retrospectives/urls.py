from django.urls import include, path

from apps.retrospectives.views import (
    ClosedRetrospectiveDetailView,
    MilestoneDetailView,
    MilestoneListCreateView,
    RetrospectiveCloseView,
    RetrospectiveDetailView,
    RetrospectiveFocusCardView,
    RetrospectiveHistoryView,
    RetrospectiveListCreateView,
    RetrospectiveNextFocusCardView,
    TeamSuggestionView,
)

urlpatterns = [
    path("retrospectives/", RetrospectiveListCreateView.as_view(), name="retrospective-list-create"),
    path("retrospectives/<uuid:pk>/", RetrospectiveDetailView.as_view(), name="retrospective-detail"),
    path("retrospectives/history/", RetrospectiveHistoryView.as_view(), name="retrospective-history"),
    path("retrospectives/<uuid:retrospective_id>/detail/", ClosedRetrospectiveDetailView.as_view(), name="closed-retrospective-detail"),
    path("retrospectives/<uuid:retrospective_id>/close/", RetrospectiveCloseView.as_view(), name="retrospective-close"),
    path("retrospectives/<uuid:retrospective_id>/focus-card/", RetrospectiveFocusCardView.as_view(), name="retrospective-focus-card"),
    path("retrospectives/<uuid:retrospective_id>/next-card/", RetrospectiveNextFocusCardView.as_view(), name="retrospective-next-card"),
    path("teams/suggestions/", TeamSuggestionView.as_view(), name="team-suggestions"),
    path("retrospectives/<uuid:retrospective_id>/milestones/", MilestoneListCreateView.as_view(), name="milestone-list-create"),
    path("retrospectives/<uuid:retrospective_id>/milestones/<uuid:milestone_id>/", MilestoneDetailView.as_view(), name="milestone-detail"),
    path("", include("apps.cards.urls")),
    path("", include("apps.actions.urls")),
]