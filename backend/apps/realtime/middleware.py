from urllib.parse import parse_qs

from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken

User = get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = None
        if 'token' in query_params:
            token = query_params['token'][0]
        else:
            for header, value in scope.get('headers', []):
                if header == b'authorization':
                    token = value.decode().split()[1]
        print(f"[JWTAuthMiddleware] Query params: {query_params}, Token: {token}")
        from asgiref.sync import sync_to_async
        if token:
            try:
                validated_token = await sync_to_async(UntypedToken)(token)
                user = await sync_to_async(JWTAuthentication().get_user)(validated_token)
                print(f"[JWTAuthMiddleware] Authenticated user: {user}")
                scope['user'] = user
            except Exception as e:
                print(f"[JWTAuthMiddleware] Token error: {e}")
                scope['user'] = AnonymousUser()
        else:
            print("[JWTAuthMiddleware] No token provided, using AnonymousUser")
            scope['user'] = AnonymousUser()
        close_old_connections()
        return await super().__call__(scope, receive, send)
