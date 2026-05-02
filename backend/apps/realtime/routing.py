from django.urls import re_path

from apps.realtime.consumers import RetrospectiveConsumer

websocket_urlpatterns = [
    re_path(r"ws/retrospectives/(?P<retrospective_id>[0-9a-f-]+)/$", RetrospectiveConsumer.as_asgi()),
]