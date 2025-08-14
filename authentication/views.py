from rest_framework import status, generics, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
import uuid
from django.db import models
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserDetailSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    DroneSerializer, DroneCreateSerializer,
    DroneFlightSerializer, DroneFlightCreateSerializer,
    CarouselImageSerializer, CarouselImageListSerializer
)
from .models import User, PasswordResetToken, Drone, DroneFlight, CarouselImage


class UserRegistrationView(generics.CreateAPIView):
    """
    View for user registration
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
    View for user login
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
    View for user logout
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
    View for retrieving and updating user profile
    """
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.GenericAPIView):
    """
    View for changing password
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'message': 'Ancien mot de passe incorrect',
                    'errors': {'old_password': ['L\'ancien mot de passe est incorrect']}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # change password
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
                

                token = str(uuid.uuid4())
                expires_at = timezone.now() + timedelta(hours=24)
                

                reset_token, created = PasswordResetToken.objects.update_or_create(
                    user=user,
                    defaults={
                        'token': token,
                        'expires_at': expires_at,
                        'is_used': False
                    }
                )
                

                return Response({
                    'message': 'Email de réinitialisation envoyé',
                    'token': token  
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


class DroneViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user's drones
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return only the drones of the connected user"""
        try:
            return Drone.objects.filter(user=self.request.user)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des drones: {e}")
            return Drone.objects.none()
    
    def get_serializer_class(self):
        """Utilise le bon sérialiseur selon l'action"""
        if self.action in ['create', 'update', 'partial_update']:
            return DroneCreateSerializer
        return DroneSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new drone with error handling"""
        try:
            logger.info(f"Tentative de création de drone avec les données: {request.data}")
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                drone = serializer.save(user=request.user)
                logger.info(f"Drone créé avec succès: {drone.id}")
                
                return Response(
                    serializer.data, 
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.error(f"Erreurs de validation: {serializer.errors}")
                return Response(
                    {'error': 'Données invalides', 'details': serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la création du drone: {e}")
            return Response(
                {'error': 'Erreur interne du serveur'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def list(self, request, *args, **kwargs):
        """List drones with error handling"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la liste des drones: {e}")
            return Response(
                {'error': 'Erreur lors de la récupération des drones'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def perform_create(self, serializer):
        """Assign automatically the connected user as owner"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Mettre à jour le statut d'un drone"""
        drone = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Drone.STATUS_CHOICES):
            return Response(
                {'error': 'Statut invalide'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        drone.status = new_status
        drone.save()
        
        return Response({
            'message': f'Statut du drone {drone.name} mis à jour vers {new_status}',
            'status': 'success'
        })
    
    @action(detail=True, methods=['post'])
    def schedule_maintenance(self, request, pk=None):
        """Programmer une maintenance pour un drone"""
        drone = self.get_object()
        maintenance_date = request.data.get('maintenance_date')
        
        if not maintenance_date:
            return Response(
                {'error': 'Date de maintenance requise'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        drone.next_maintenance = maintenance_date
        drone.save()
        
        return Response({
            'message': f'Maintenance programmée pour {drone.name} le {maintenance_date}',
            'status': 'success'
        })


class DroneFlightViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les vols de drones
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Retourne les vols des drones de l'utilisateur connecté"""
        try:
            return DroneFlight.objects.filter(
                drone__user=self.request.user
            ).select_related('drone', 'pilot')
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des vols: {e}")
            return DroneFlight.objects.none()
    
    def get_serializer_class(self):
        """Utilise le bon sérialiseur selon l'action"""
        if self.action in ['create', 'update', 'partial_update']:
            return DroneFlightCreateSerializer
        return DroneFlightSerializer
    
    def create(self, request, *args, **kwargs):
        """Créer un nouveau vol avec gestion d'erreurs améliorée"""
        try:
            logger.info(f"Tentative de création de vol avec les données: {request.data}")
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                # Vérifier que le drone appartient à l'utilisateur
                drone_id = serializer.validated_data.get('drone')
                if not drone_id:
                    return Response(
                        {'error': 'Le drone est requis'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                try:
                    drone = get_object_or_404(Drone, id=drone_id.id, user=request.user)
                except Exception as e:
                    logger.error(f"Erreur lors de la récupération du drone {drone_id.id}: {e}")
                    return Response(
                        {'error': 'Drone non trouvé ou non autorisé'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # create the flight
                flight = serializer.save(pilot=request.user)
                logger.info(f"Vol créé avec succès: {flight.id}")
                
                return Response(
                    serializer.data, 
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.error(f"Erreurs de validation: {serializer.errors}")
                return Response(
                    {'error': 'Données invalides', 'details': serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la création du vol: {e}")
            return Response(
                {'error': 'Erreur interne du serveur'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def list(self, request, *args, **kwargs):
        """List flights with error handling"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la liste des vols: {e}")
            return Response(
                {'error': 'Erreur lors de la récupération des vols'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def drone_stats(self, request):
        """Get the statistics of flights by drone"""
        try:
            user_drones = Drone.objects.filter(user=request.user)
            stats = []
            
            for drone in user_drones:
                flights = DroneFlight.objects.filter(drone=drone)
                total_flights = flights.count()
                total_duration = flights.aggregate(
                    total=models.Sum('duration')
                )['total'] or 0
                
                stats.append({
                    'drone_name': drone.name,
                    'total_flights': total_flights,
                    'total_duration': total_duration,
                    'last_flight': flights.order_by('-flight_date').first().flight_date if flights.exists() else None
                })
            
            return Response({
                'stats': stats,
                'status': 'success'
            })
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return Response(
                {'error': 'Erreur lors de la récupération des statistiques'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def recent_flights(self, request):
        """Get recent flights"""
        try:
            recent_flights = self.get_queryset().order_by('-flight_date')[:10]
            serializer = DroneFlightSerializer(recent_flights, many=True)
            
            return Response({
                'recent_flights': serializer.data,
                'status': 'success'
            })
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des vols récents: {e}")
            return Response(
                {'error': 'Erreur lors de la récupération des vols récents'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CarouselImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des images de carrousel
    """
    queryset = CarouselImage.objects.filter(is_active=True).order_by('order', 'created_at')
    serializer_class = CarouselImageSerializer
    permission_classes = [permissions.AllowAny]  # Public pour l'affichage
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CarouselImageListSerializer
        return CarouselImageSerializer
    
    def list(self, request, *args, **kwargs):
        """Liste publique des images de carrousel actives"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'images': serializer.data,
                'count': queryset.count(),
                'status': 'success'
            })
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des images de carrousel: {e}")
            return Response(
                {'error': 'Erreur lors de la récupération des images'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        """Créer une nouvelle image de carrousel (admin seulement)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Accès non autorisé'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Image de carrousel créée avec succès',
                'image': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': 'Données invalides',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Mettre à jour une image de carrousel (admin seulement)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Accès non autorisé'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Supprimer une image de carrousel (admin seulement)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Accès non autorisé'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)
