from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer, GoogleLoginSerializer
from rest_framework.authtoken.models import Token
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GoogleLoginView(APIView):
    """
    Vue pour gérer la connexion via Google OAuth2.
    """
    def post(self, request, *args, **kwargs):
        serializer = GoogleLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    Vue pour gérer la connexion classique.
    """
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # Retourner la réponse après validation
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        # Si les données ne sont pas valides, retourner les erreurs
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)