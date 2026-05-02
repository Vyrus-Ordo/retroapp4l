from django.urls import path

from apps.cards.views import (
    CardDetailView,
    CardGroupView,
    CardListCreateView,
    CardUngroupView,
    CardVoteView,
    VoteListView,
    VotesConfigView,
)

urlpatterns = [
    path(
        "retrospectives/<uuid:retrospective_id>/cards/",
        CardListCreateView.as_view(),
        name="card-list-create",
    ),
    path(
        "retrospectives/<uuid:retrospective_id>/cards/<uuid:card_id>/",
        CardDetailView.as_view(),
        name="card-detail",
    ),
    path(
        "retrospectives/<uuid:retrospective_id>/cards/group/",
        CardGroupView.as_view(),
        name="card-group",
    ),
    path(
        "retrospectives/<uuid:retrospective_id>/cards/<uuid:card_id>/ungroup/",
        CardUngroupView.as_view(),
        name="card-ungroup",
    ),
    path(
        "retrospectives/<uuid:retrospective_id>/cards/<uuid:card_id>/vote/",
        CardVoteView.as_view(),
        name="card-vote",
    ),
    path(
        "retrospectives/<uuid:retrospective_id>/votes/",
        VoteListView.as_view(),
        name="vote-list",
    ),
    path(
        "retrospectives/<uuid:retrospective_id>/votes-config/",
        VotesConfigView.as_view(),
        name="votes-config",
    ),
]
