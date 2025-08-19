from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.conf import settings
from django.http import HttpResponse
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class JWTTokenManager:
    """
    Gestionnaire de tokens JWT avec cookies HttpOnly
    """
    
    @staticmethod
    def create_tokens_for_user(user):
        """
        Créer les tokens d'accès et de rafraîchissement pour un utilisateur
        """
        try:
            refresh = RefreshToken.for_user(user)
            
            # Ajouter des claims personnalisés
            refresh['user_id'] = str(user.id)
            refresh['email'] = user.email
            refresh['username'] = user.username
            refresh['is_staff'] = user.is_staff
            refresh['is_superuser'] = user.is_superuser
            
            access_token = refresh.access_token
            access_token['user_id'] = str(user.id)
            access_token['email'] = user.email
            access_token['username'] = user.username
            access_token['is_staff'] = user.is_staff
            access_token['is_superuser'] = user.is_superuser
            
            return {
                'access': str(access_token),
                'refresh': str(refresh),
                'access_expires': access_token.current_time + access_token.lifetime,
                'refresh_expires': refresh.current_time + refresh.lifetime
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création des tokens JWT: {e}")
            raise
    
    @staticmethod
    def set_auth_cookies(response, tokens):
        """
        Définir les cookies d'authentification HttpOnly
        """
        try:
            # Cookie d'accès (courte durée)
            response.set_cookie(
                'access_token',
                tokens['access'],
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                httponly=True,
                secure=not settings.DEBUG,  # HTTPS en production
                samesite='Lax',
                path='/'
            )
            
            # Cookie de rafraîchissement (longue durée)
            response.set_cookie(
                'refresh_token',
                tokens['refresh'],
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
                httponly=True,
                secure=not settings.DEBUG,  # HTTPS en production
                samesite='Lax',
                path='/'
            )
            
            # Cookie pour vérifier l'état d'authentification côté client
            response.set_cookie(
                'is_authenticated',
                'true',
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                httponly=False,  # Accessible côté client
                secure=not settings.DEBUG,
                samesite='Lax',
                path='/'
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors de la définition des cookies: {e}")
            raise
    
    @staticmethod
    def clear_auth_cookies(response):
        """
        Supprimer tous les cookies d'authentification
        """
        try:
            response.delete_cookie('access_token', path='/')
            response.delete_cookie('refresh_token', path='/')
            response.delete_cookie('is_authenticated', path='/')
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression des cookies: {e}")
            raise
    
    @staticmethod
    def refresh_access_token(refresh_token_str):
        """
        Rafraîchir le token d'accès
        """
        try:
            refresh = RefreshToken(refresh_token_str)
            access_token = refresh.access_token
            
            # Ajouter les claims personnalisés
            access_token['user_id'] = refresh['user_id']
            access_token['email'] = refresh['email']
            access_token['username'] = refresh['username']
            access_token['is_staff'] = refresh['is_staff']
            access_token['is_superuser'] = refresh['is_superuser']
            
            return {
                'access': str(access_token),
                'access_expires': access_token.current_time + access_token.lifetime
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement du token: {e}")
            raise
    
    @staticmethod
    def is_token_expired(token_str):
        """
        Vérifier si un token est expiré
        """
        try:
            token = AccessToken(token_str)
            return token.current_time >= token.current_time + token.lifetime
            
        except Exception:
            return True
    
    @staticmethod
    def get_token_payload(token_str):
        """
        Récupérer le payload d'un token (sans vérification de signature)
        """
        try:
            import jwt
            payload = jwt.decode(
                token_str, 
                options={"verify_signature": False}
            )
            return payload
            
        except Exception as e:
            logger.error(f"Erreur lors du décodage du token: {e}")
            return None


class JWTCookieResponse(HttpResponse):
    """
    Réponse HTTP personnalisée avec gestion des cookies JWT
    """
    
    def __init__(self, data=None, status=200, tokens=None, **kwargs):
        super().__init__(data, status=status, **kwargs)
        
        if tokens:
            self = JWTTokenManager.set_auth_cookies(self, tokens)
    
    def set_auth_cookies(self, tokens):
        """
        Définir les cookies d'authentification
        """
        return JWTTokenManager.set_auth_cookies(self, tokens)
    
    def clear_auth_cookies(self):
        """
        Supprimer les cookies d'authentification
        """
        return JWTTokenManager.clear_auth_cookies(self)
