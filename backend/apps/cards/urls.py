from django.urls import path

from apps.cards.views import CardDetailView, CardListCreateView

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
]
