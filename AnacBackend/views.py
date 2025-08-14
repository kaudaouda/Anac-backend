from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
@permission_classes([AllowAny])
def public_endpoint(request):
    """
    Endpoint public accessible sans authentification
    """
    return Response({
        'message': 'Cet endpoint est public et accessible sans authentification',
        'status': 'success'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_endpoint(request):
    """
    Endpoint protégé nécessitant une authentification JWT
    """
    return Response({
        'message': 'Cet endpoint est protégé et nécessite une authentification JWT',
        'user_id': request.user.id,
        'username': request.user.username,
        'status': 'success'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Endpoint pour récupérer le profil utilisateur
    """
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'date_joined': user.date_joined,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'status': 'success'
    })
