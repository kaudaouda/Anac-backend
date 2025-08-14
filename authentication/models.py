from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid


class UserManager(BaseUserManager):
    """
    Gestionnaire personnalisé pour le modèle User
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Créer un utilisateur avec email et mot de passe
        """
        if not email:
            raise ValueError('L\'email est requis')
        
        # Normaliser l'email
        email = self.normalize_email(email)
        
        # Générer un username unique si non fourni
        if 'username' not in extra_fields:
            extra_fields['username'] = f"user_{uuid.uuid4().hex[:8]}"
        
        # Créer l'utilisateur
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Créer un superutilisateur
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
    Modèle utilisateur personnalisé avec UUID et champs supplémentaires
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Numéro de téléphone")
    is_verified = models.BooleanField(default=False, verbose_name="Email vérifié")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    # Remplacer username par email pour la connexion
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    # Utiliser notre gestionnaire personnalisé
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
        # Générer un username unique si non fourni
        if not self.username:
            self.username = f"user_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """
    Profil utilisateur étendu
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
    Token pour la réinitialisation du mot de passe
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
