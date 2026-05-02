from django.contrib.auth import authenticate
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import LoginSerializer, RegisterSerializer, UserSerializer


class RegisterView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		serializer = RegisterSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		refresh = RefreshToken.for_user(user)
		return Response(
			{
				"user": UserSerializer(user).data,
				"access": str(refresh.access_token),
				"refresh": str(refresh),
			},
			status=status.HTTP_201_CREATED,
		)


class LoginView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		serializer = LoginSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = authenticate(
			request=request,
			username=serializer.validated_data["email"],
			password=serializer.validated_data["password"],
		)
		if user is None:
			raise serializers.ValidationError({"detail": "Invalid credentials."})
		if user.is_guest:
			raise serializers.ValidationError({"detail": "Guest sessions must be started from an invite link."})

		refresh = RefreshToken.for_user(user)
		return Response(
			{
				"user": UserSerializer(user).data,
				"access": str(refresh.access_token),
				"refresh": str(refresh),
			}
		)


class LogoutView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		refresh_token = request.data.get("refresh")
		if not refresh_token:
			raise serializers.ValidationError({"refresh": "This field is required."})

		try:
			RefreshToken(refresh_token).blacklist()
		except TokenError as error:
			raise serializers.ValidationError({"refresh": str(error)}) from error

		return Response(status=status.HTTP_204_NO_CONTENT)

# Create your views here.
