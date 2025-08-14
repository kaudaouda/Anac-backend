from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'authentication'

# Router for the ViewSets
router = DefaultRouter()
router.register(r'carousel', views.CarouselImageViewSet, basename='carousel')

urlpatterns = [
    # Authentication routes
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('check-auth/', views.check_auth_status, name='check_auth'),
    path('refresh-token/', views.refresh_token_view, name='refresh_token'),
    
    # Carousel routes
    path('', include(router.urls)),
]
