from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.conf import settings
import jwt
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class CustomJWTAuthentication(JWTAuthentication):
    """
    Authentification JWT personnalisée avec gestion des cookies HttpOnly
    """
    
    def authenticate(self, request):
        """
        Authentifier l'utilisateur via le cookie JWT
        """
        try:
            # Récupérer le token depuis le cookie
            access_token = request.COOKIES.get('access_token')
            
            if not access_token:
                return None
            
            # Valider le token
            validated_token = self.get_validated_token(access_token)
            
            # Récupérer l'utilisateur
            user = self.get_user(validated_token)
            
            if not user.is_active:
                return None
                
            return (user, validated_token)
            
        except (InvalidToken, TokenError) as e:
            logger.warning(f"Token JWT invalide: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification JWT: {e}")
            return None
    
    def get_validated_token(self, raw_token):
        """
        Valider et décoder le token JWT
        """
        try:
            # Décoder le token sans vérification pour obtenir les claims
            unverified_payload = jwt.decode(
                raw_token, 
                options={"verify_signature": False}
            )
            
            # Vérifier l'expiration
            exp_timestamp = unverified_payload.get('exp')
            if exp_timestamp:
                exp_datetime = datetime.fromtimestamp(exp_timestamp)
                if exp_datetime < datetime.now():
                    raise InvalidToken("Token expiré")
            
            # Vérifier la signature et valider le token
            validated_token = AccessToken(raw_token)
            return validated_token
            
        except jwt.ExpiredSignatureError:
            raise InvalidToken("Token expiré")
        except jwt.InvalidTokenError as e:
            raise InvalidToken(f"Token invalide: {e}")
        except Exception as e:
            raise InvalidToken(f"Erreur de validation du token: {e}")
    
    def get_user(self, validated_token):
        """
        Récupérer l'utilisateur à partir du token validé
        """
        try:
            user_id = validated_token.get('user_id')
            if user_id is None:
                raise InvalidToken("Token ne contient pas d'ID utilisateur")
            
            user = User.objects.get(id=user_id)
            return user
            
        except User.DoesNotExist:
            raise InvalidToken("Utilisateur non trouvé")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
            raise InvalidToken("Erreur lors de la récupération de l'utilisateur")


class JWTCookieAuthentication(CustomJWTAuthentication):
    """
    Authentification JWT avec gestion automatique des cookies
    """
    
    def authenticate_header(self, request):
        """
        Retourner l'en-tête d'authentification pour les erreurs 401
        """
        return 'Bearer realm="api"'
