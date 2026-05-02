from django.urls import include, path

from apps.retrospectives.views import (
    MilestoneDetailView,
    MilestoneListCreateView,
    RetrospectiveDetailView,
    RetrospectiveListCreateView,
    TeamSuggestionView,
)

urlpatterns = [
    path("retrospectives/", RetrospectiveListCreateView.as_view(), name="retrospective-list-create"),
    path("retrospectives/<uuid:pk>/", RetrospectiveDetailView.as_view(), name="retrospective-detail"),
    path("teams/suggestions/", TeamSuggestionView.as_view(), name="team-suggestions"),
    path("retrospectives/<uuid:retrospective_id>/milestones/", MilestoneListCreateView.as_view(), name="milestone-list-create"),
    path("retrospectives/<uuid:retrospective_id>/milestones/<uuid:milestone_id>/", MilestoneDetailView.as_view(), name="milestone-detail"),
    path("", include("apps.cards.urls")),
]