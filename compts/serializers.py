from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
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
    access_token = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validation et création d'utilisateur via un accès Google.
        """
        request = self.context.get('request')
        email = request.data.get('email')
        name = request.data.get('name')
        picture = request.data.get('picture')

        if not email:
            raise serializers.ValidationError("L'email est requis pour procéder.")

        provider = GoogleProvider.id  # Identifiant du fournisseur Google

        # Vérifiez si un compte SocialAccount existe
        social_account = SocialAccount.objects.filter(provider=provider, user__email=email).first()
        if social_account:
            # Si le compte existe, renvoyer les données de l'utilisateur
            return {"email": email, "name": name, "picture": picture}

        # Si aucun compte SocialAccount n'existe, créer un nouvel utilisateur
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            # Créer un utilisateur avec les informations Google
            user = CustomUser.objects.create_user(
                username=email.split("@")[0],  # Générer un username basé sur l'email
                email=email,
                password=None,  # Aucun mot de passe, connexion via Google uniquement
            )

        # Ajouter le SocialAccount lié
        SocialAccount.objects.create(
            user=user,
            provider=provider,
            extra_data={
                "name": name,
                "picture": picture,
            },
        )

        return {"email": email, "name": name, "picture": picture}

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        return user