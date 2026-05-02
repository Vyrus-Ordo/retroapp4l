from django.urls import path

from apps.retrospectives.views import RetrospectiveDetailView, RetrospectiveListCreateView, TeamSuggestionView

urlpatterns = [
    path("retrospectives/", RetrospectiveListCreateView.as_view(), name="retrospective-list-create"),
    path("retrospectives/<uuid:pk>/", RetrospectiveDetailView.as_view(), name="retrospective-detail"),
    path("teams/suggestions/", TeamSuggestionView.as_view(), name="team-suggestions"),
]