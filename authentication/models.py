from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid


class UserManager(BaseUserManager):
    """
    Custom user manager for the User model
    """
    
    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError('L\'email est requis')
        
        email = self.normalize_email(email)
        
        if 'username' not in extra_fields:
            extra_fields['username'] = f"user_{uuid.uuid4().hex[:8]}"
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create a superuser
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model with UUID and additional fields
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Numéro de téléphone")
    is_verified = models.BooleanField(default=False, verbose_name="Email vérifié")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        db_table = 'auth_user'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = f"user_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """
    User profile model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Photo de profil")
    bio = models.TextField(blank=True, verbose_name="Biographie")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Date de naissance")
    address = models.TextField(blank=True, verbose_name="Adresse")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    country = models.CharField(max_length=100, blank=True, verbose_name="Pays")
    postal_code = models.CharField(max_length=10, blank=True, verbose_name="Code postal")
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
        db_table = 'user_profile'
    
    def __str__(self):
        return f"Profil de {self.user.full_name}"


class PasswordResetToken(models.Model):
    """
    Password reset token model
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Token de réinitialisation"
        verbose_name_plural = "Tokens de réinitialisation"
        db_table = 'password_reset_token'
    
    def __str__(self):
        return f"Token pour {self.user.email}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at


class Drone(models.Model):
    """
    Drone model for users to manage their drones
    """
    DRONE_TYPES = [
        ('quadcopter', 'Quadricoptère'),
        ('hexacopter', 'Hexacoptère'),
        ('octocopter', 'Octocoptère'),
        ('fixed_wing', 'Aile fixe'),
        ('helicopter', 'Hélicoptère'),
        ('other', 'Autre'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('maintenance', 'En maintenance'),
        ('inactive', 'Inactif'),
        ('retired', 'Retiré'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drones', verbose_name="Propriétaire")
    name = models.CharField(max_length=100, verbose_name="Nom du drone")
    model = models.CharField(max_length=100, verbose_name="Modèle")
    brand = models.CharField(max_length=100, blank=True, verbose_name="Marque")
    drone_type = models.CharField(max_length=20, choices=DRONE_TYPES, verbose_name="Type de drone")
    serial_number = models.CharField(max_length=100, blank=True, verbose_name="Numéro de série")
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="Poids (kg)")
    max_payload = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="Charge utile max (kg)")
    max_flight_time = models.IntegerField(blank=True, null=True, verbose_name="Temps de vol max (minutes)")
    max_range = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Portée max (km)")
    max_altitude = models.IntegerField(blank=True, null=True, verbose_name="Altitude max (m)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Statut")
    registration_number = models.CharField(max_length=50, blank=True, verbose_name="Numéro d'enregistrement")
    insurance_info = models.TextField(blank=True, verbose_name="Informations d'assurance")
    maintenance_notes = models.TextField(blank=True, verbose_name="Notes de maintenance")
    purchase_date = models.DateField(blank=True, null=True, verbose_name="Date d'achat")
    last_maintenance = models.DateField(blank=True, null=True, verbose_name="Dernière maintenance")
    next_maintenance = models.DateField(blank=True, null=True, verbose_name="Prochaine maintenance")
    photo = models.ImageField(upload_to='drones/', blank=True, null=True, verbose_name="Photo du drone")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Drone"
        verbose_name_plural = "Drones"
        db_table = 'drone'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.full_name}"
    
    @property
    def is_maintenance_due(self):
        """Check if maintenance is due"""
        from django.utils import timezone
        if self.next_maintenance:
            return timezone.now().date() >= self.next_maintenance
        return False
    
    @property
    def age_in_days(self):
        """Calculate drone age in days"""
        from django.utils import timezone
        if self.purchase_date:
            return (timezone.now().date() - self.purchase_date).days
        return None


class DroneFlight(models.Model):
    """
    Flight log for drones
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    drone = models.ForeignKey(Drone, on_delete=models.CASCADE, related_name='flights', verbose_name="Drone")
    pilot = models.ForeignKey(User, on_delete=models.CASCADE, related_name='piloted_flights', verbose_name="Pilote")
    flight_date = models.DateTimeField(verbose_name="Date et heure de vol")
    duration = models.IntegerField(verbose_name="Durée du vol (minutes)")
    location = models.CharField(max_length=200, verbose_name="Lieu de vol")
    purpose = models.CharField(max_length=200, blank=True, verbose_name="Objectif du vol")
    weather_conditions = models.TextField(blank=True, verbose_name="Conditions météo")
    notes = models.TextField(blank=True, verbose_name="Notes de vol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Vol de drone"
        verbose_name_plural = "Vols de drones"
        db_table = 'drone_flight'
        ordering = ['-flight_date']
    
    def __str__(self):
        return f"Vol de {self.drone.name} le {self.flight_date.strftime('%d/%m/%Y')}"


class CarouselImage(models.Model):
    """
    Modèle pour les images du carrousel de la page d'accueil
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Titre de l'image")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='carousel/', verbose_name="Image")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Image de carrousel"
        verbose_name_plural = "Images de carrousel"
        db_table = 'carousel_image'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.title} (Ordre: {self.order})"
    
    @property
    def image_url(self):
        """Retourne l'URL de l'image"""
        if self.image:
            return self.image.url
        return None


class Airport(models.Model):
    """
    Modèle pour les aéroports et aérodromes de la Côte d'Ivoire
    """
    AIRPORT_TYPES = [
        ('international', 'Aéroport International'),
        ('domestic', 'Aéroport Domestique'),
        ('aerodrome', 'Aérodrome'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    airport_id = models.CharField(max_length=10, unique=True, verbose_name="Identifiant unique de l'aéroport")
    name = models.CharField(max_length=200, verbose_name="Nom de l'aéroport")
    code = models.CharField(max_length=10, blank=True, verbose_name="Code IATA")
    airport_type = models.CharField(max_length=20, choices=AIRPORT_TYPES, verbose_name="Type d'aéroport")
    city = models.CharField(max_length=100, verbose_name="Ville")
    latitude = models.DecimalField(max_digits=10, decimal_places=6, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=10, decimal_places=6, verbose_name="Longitude")
    radius = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Rayon de la zone interdite (km)")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=False, verbose_name="Approuvé par l'admin")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Aéroport/Aérodrome"
        verbose_name_plural = "Aéroports/Aérodromes"
        db_table = 'airport'
        ordering = ['airport_type', 'name']
        indexes = [
            models.Index(fields=['airport_type']),
            models.Index(fields=['city']),
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.city}) - {self.get_airport_type_display()}"

    @property
    def coordinates(self):
        return [float(self.latitude), float(self.longitude)]

    @property
    def is_restricted_zone(self):
        return self.airport_type in ['international', 'domestic', 'aerodrome']


class NaturalReserve(models.Model):
    """
    Modèle pour les réserves naturelles de la Côte d'Ivoire
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reserve_id = models.CharField(max_length=20, unique=True, verbose_name="Identifiant unique de la réserve")
    name = models.CharField(max_length=200, verbose_name="Nom de la réserve")
    type = models.CharField(max_length=50, default='natural_reserve', verbose_name="Type de zone")
    area = models.CharField(max_length=50, verbose_name="Superficie")
    description = models.TextField(blank=True, verbose_name="Description")
    coordinates = models.JSONField(verbose_name="Coordonnées GPS", help_text="Liste de coordonnées [lat, lng]")
    is_active = models.BooleanField(default=False, verbose_name="Approuvé par l'admin")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Réserve naturelle"
        verbose_name_plural = "Réserves naturelles"
        db_table = 'natural_reserve'
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.area})"
    
    @property
    def formatted_coordinates(self):
        """Retourne les coordonnées au format Leaflet"""
        if self.coordinates:
            return [[float(coord[0]), float(coord[1])] for coord in self.coordinates]
        return []


class NationalPark(models.Model):
    """
    Modèle pour les parcs nationaux de la Côte d'Ivoire
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    park_id = models.CharField(max_length=20, unique=True, verbose_name="Identifiant unique du parc")
    name = models.CharField(max_length=200, verbose_name="Nom du parc")
    type = models.CharField(max_length=50, default='national_park', verbose_name="Type de zone")
    area = models.CharField(max_length=50, verbose_name="Superficie")
    description = models.TextField(blank=True, verbose_name="Description")
    coordinates = models.JSONField(verbose_name="Coordonnées GPS", help_text="Liste de coordonnées [lat, lng]")
    is_active = models.BooleanField(default=False, verbose_name="Approuvé par l'admin")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Parc national"
        verbose_name_plural = "Parcs nationaux"
        db_table = 'national_park'
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.area})"
    
    @property
    def formatted_coordinates(self):
        """Retourne les coordonnées au format Leaflet"""
        if self.coordinates:
            return [[float(coord[0]), float(coord[1])] for coord in self.coordinates]
        return []


class ProtectedAreaCoordinates(models.Model):
    """
    Modèle pour stocker les coordonnées des zones protégées
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    natural_reserve = models.ForeignKey(NaturalReserve, on_delete=models.CASCADE, related_name='old_coordinates', null=True, blank=True)
    national_park = models.ForeignKey(NationalPark, on_delete=models.CASCADE, related_name='old_coordinates', null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=10, decimal_places=6, verbose_name="Longitude")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre des coordonnées")
    is_active = models.BooleanField(default=False, verbose_name="Approuvé par l'admin")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    def clean(self):
        """Validation personnalisée"""
        from django.core.exceptions import ValidationError
        
        # Vérifier qu'exactement une zone est associée
        if bool(self.natural_reserve) == bool(self.national_park):
            raise ValidationError(
                'Une coordonnée doit être associée à exactement une zone protégée (réserve naturelle OU parc national)'
            )
        
        # Vérifier que les coordonnées sont valides
        if self.latitude < -90 or self.latitude > 90:
            raise ValidationError('La latitude doit être comprise entre -90 et 90')
        
        if self.longitude < -180 or self.longitude > 180:
            raise ValidationError('La longitude doit être comprise entre -180 et 180')
    
    def save(self, *args, **kwargs):
        """Validation avant sauvegarde"""
        self.clean()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Coordonnées de zone protégée"
        verbose_name_plural = "Coordonnées des zones protégées"
        db_table = 'protected_area_coordinates'
        ordering = ['order']
        indexes = [
            models.Index(fields=['natural_reserve', 'order']),
            models.Index(fields=['national_park', 'order']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        if self.natural_reserve:
            return f"Coordonnée {self.order} - {self.natural_reserve.name}"
        elif self.national_park:
            return f"Coordonnée {self.order} - {self.national_park.name}"
        return f"Coordonnée {self.order}"


class JWTBlacklistedToken(models.Model):
    """
    Modèle pour stocker les tokens JWT blacklistés
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.TextField(unique=True, verbose_name="Token JWT blacklisté")
    blacklisted_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de blacklist")
    expires_at = models.DateTimeField(verbose_name="Date d'expiration")
    user_id = models.UUIDField(verbose_name="ID de l'utilisateur")
    token_type = models.CharField(
        max_length=10, 
        choices=[
            ('access', 'Token d\'accès'),
            ('refresh', 'Token de rafraîchissement')
        ],
        verbose_name="Type de token"
    )
    reason = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name="Raison du blacklist"
    )
    
    class Meta:
        verbose_name = "Token JWT blacklisté"
        verbose_name_plural = "Tokens JWT blacklistés"
        db_table = 'jwt_blacklisted_token'
        ordering = ['-blacklisted_at']
        indexes = [
            models.Index(fields=['user_id'], name='jwt_blackli_user_id_idx'),
            models.Index(fields=['token_type'], name='jwt_blackli_token_ty_idx'),
            models.Index(fields=['expires_at'], name='jwt_blackli_expires_idx'),
        ]
    
    def __str__(self):
        return f"Token {self.token_type} blacklisté pour l'utilisateur {self.user_id}"
    
    @property
    def is_expired(self):
        """Vérifier si le token est expiré"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
