from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import timedelta
import uuid

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserDetailSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer
)
from .models import User, PasswordResetToken


class UserRegistrationView(generics.CreateAPIView):
    """
    Vue pour l'inscription d'un nouvel utilisateur
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Générer les tokens JWT
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Compte créé avec succès',
                'user': UserDetailSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'message': 'Erreur lors de la création du compte',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(generics.GenericAPIView):
    """
    Vue pour la connexion utilisateur
    """
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Générer les tokens JWT
            refresh = RefreshToken.for_user(user)
            
            # Mettre à jour la dernière connexion
            user.last_login = timezone.now()
            user.save()
            
            return Response({
                'message': 'Connexion réussie',
                'user': UserDetailSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'Identifiants invalides',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(generics.GenericAPIView):
    """
    Vue pour la déconnexion utilisateur
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Récupérer le token de rafraîchissement depuis le body
            refresh_token = request.data.get('refresh_token')
            
            if refresh_token:
                # Invalider le token de rafraîchissement
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Déconnexion réussie'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'message': 'Erreur lors de la déconnexion',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Vue pour récupérer et mettre à jour le profil utilisateur
    """
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.GenericAPIView):
    """
    Vue pour changer le mot de passe
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Vérifier l'ancien mot de passe
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'message': 'Ancien mot de passe incorrect',
                    'errors': {'old_password': ['L\'ancien mot de passe est incorrect']}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Changer le mot de passe
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'message': 'Mot de passe modifié avec succès'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'Erreur lors de la modification du mot de passe',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(generics.GenericAPIView):
    """
    Vue pour demander la réinitialisation du mot de passe
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email, is_active=True)
                
                # Générer un token unique
                token = str(uuid.uuid4())
                expires_at = timezone.now() + timedelta(hours=24)
                
                # Créer ou mettre à jour le token
                reset_token, created = PasswordResetToken.objects.update_or_create(
                    user=user,
                    defaults={
                        'token': token,
                        'expires_at': expires_at,
                        'is_used': False
                    }
                )
                
                # Ici vous pouvez envoyer un email avec le token
                # Pour l'instant, on retourne le token (en production, envoyez un email)
                
                return Response({
                    'message': 'Email de réinitialisation envoyé',
                    'token': token  # En production, ne pas retourner le token
                }, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                return Response({
                    'message': 'Aucun utilisateur trouvé avec cet email'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'message': 'Erreur lors de la demande de réinitialisation',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_auth_status(request):
    """
    Vérifier le statut d'authentification de l'utilisateur
    """
    return Response({
        'is_authenticated': True,
        'user': UserDetailSerializer(request.user).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def refresh_token_view(request):
    """
    Rafraîchir le token d'accès
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({
                'message': 'Token de rafraîchissement requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Valider et rafraîchir le token
        token = RefreshToken(refresh_token)
        new_access_token = str(token.access_token)
        
        return Response({
            'access': new_access_token,
            'refresh': refresh_token
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'message': 'Token de rafraîchissement invalide',
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
