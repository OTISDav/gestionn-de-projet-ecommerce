from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google.provider import GoogleProvider
from django.contrib.auth import get_user_model


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

CustomUser = get_user_model()



class GoogleLoginSerializer(serializers.Serializer):
    """
    Sérialiseur pour la connexion avec Google OAuth2.
    """
    access_token = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validation et création d'un utilisateur via Google OAuth2.
        """
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        try:
            # Vérifier le jeton Google
            idinfo = id_token.verify_oauth2_token(data['access_token'], google_requests.Request())

            email = idinfo.get('email')
            name = idinfo.get('name')
            picture = idinfo.get('picture')

            if not email:
                raise serializers.ValidationError("Email non fourni par Google.")

            # Rechercher ou créer un utilisateur
            user, created = CustomUser.objects.get_or_create(email=email, defaults={
                'username': email.split('@')[0],
                'is_active': True,
            })

            # Générer les tokens JWT
            refresh = RefreshToken.for_user(user)

            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_data': {
                    'id': user.id,
                    'email': user.email,
                    'name': name,
                    'picture': picture,
                }
            }

        except ValueError as e:
            raise serializers.ValidationError(f"Jeton Google invalide : {e}")


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Identifiants invalides.")

        if not user.is_active:
            raise serializers.ValidationError("Ce compte est inactif.")

        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
            }
        }