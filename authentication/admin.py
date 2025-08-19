from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User, UserProfile, PasswordResetToken, Drone, DroneFlight, 
    CarouselImage, Airport, NaturalReserve, NationalPark, JWTBlacklistedToken
)


class UserProfileInline(admin.StackedInline):
    """
    Inline for the user profile
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ['avatar', 'bio', 'birth_date', 'address', 'city', 'country', 'postal_code']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Administration of users
    """
    inlines = [UserProfileInline]
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_verified', 'created_at')
    list_filter = ('is_staff', 'is_active', 'is_verified', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'phone', 'username')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Nom complet'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'country', 'has_avatar')
    list_filter = ('country', 'city', 'birth_date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'city', 'country')
    readonly_fields = ('user',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    
    def user_full_name(self, obj):
        return obj.user.full_name
    user_full_name.short_description = 'Nom complet'
    
    def has_avatar(self, obj):
        return bool(obj.avatar)
    has_avatar.boolean = True
    has_avatar.short_description = 'A un avatar'


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Administration of password reset tokens
    """
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used', 'is_expired')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__email', 'token')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email utilisateur'
    
    def token_preview(self, obj):
        return f"{obj.token[:8]}..."
    token_preview.short_description = 'Token'
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expiré'


@admin.register(Drone)
class DroneAdmin(admin.ModelAdmin):
    """
    Administration of drones
    """
    list_display = ('name', 'user', 'drone_type', 'status', 'created_at')
    list_filter = ('drone_type', 'status', 'created_at', 'purchase_date')
    search_fields = ('name', 'user__email', 'serial_number', 'registration_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'model', 'brand', 'drone_type', 'serial_number')
        }),
        ('Spécifications techniques', {
            'fields': ('weight', 'max_payload', 'max_flight_time', 'max_range', 'max_altitude')
        }),
        ('Gestion et statut', {
            'fields': ('status', 'registration_number', 'insurance_info')
        }),
        ('Maintenance', {
            'fields': ('maintenance_notes', 'purchase_date', 'last_maintenance', 'next_maintenance')
        }),
        ('Média', {
            'fields': ('photo',)
        }),
        ('Informations système', {
            'fields': ('id', 'user', 'created_at', 'updated_at', 'is_maintenance_due', 'age_in_days'),
            'classes': ('collapse',)
        }),
    )
    
    def user_full_name(self, obj):
        return obj.user.full_name
    user_full_name.short_description = 'Propriétaire'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    
    def is_maintenance_due(self, obj):
        if obj.is_maintenance_due:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Maintenance requise</span>')
        return format_html('<span style="color: green;">✓ OK</span>')
    is_maintenance_due.short_description = 'Maintenance'


@admin.register(DroneFlight)
class DroneFlightAdmin(admin.ModelAdmin):
    """
    Administration of drone flights
    """
    list_display = ('drone', 'pilot', 'flight_date', 'duration', 'location')
    list_filter = ('flight_date', 'drone__drone_type', 'created_at')
    search_fields = ('drone__name', 'pilot__email', 'location', 'purpose')
    ordering = ('-flight_date',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Informations de vol', {
            'fields': ('drone', 'pilot', 'flight_date', 'duration', 'location')
        }),
        ('Détails', {
            'fields': ('purpose', 'weather_conditions', 'notes')
        }),
        ('Informations système', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def drone_name(self, obj):
        return obj.drone.name
    drone_name.short_description = 'Drone'
    
    def pilot_full_name(self, obj):
        return obj.pilot.full_name
    pilot_full_name.short_description = 'Pilote'


@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    """
    Administration of carousel images
    """
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'order', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('order', 'created_at')
    list_editable = ('order', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'description', 'image')
        }),
        ('Affichage', {
            'fields': ('order', 'is_active')
        }),
        ('Informations système', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px; object-fit: cover;" />',
                obj.image.url
            )
        return format_html('<span style="color: red;">Aucune image</span>')
    image_preview.short_description = 'Aperçu'


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    """Administration des aéroports et aérodromes"""
    list_display = ('name', 'city', 'airport_type', 'is_active', 'created_at')
    list_filter = ('airport_type', 'is_active', 'city', 'created_at')
    search_fields = ('name', 'city', 'code', 'airport_id')
    ordering = ('airport_type', 'name')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('airport_id', 'name', 'code', 'airport_type', 'city')
        }),
        ('Coordonnées', {
            'fields': ('latitude', 'longitude', 'radius')
        }),
        ('Détails', {
            'fields': ('description', 'is_active')
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(NaturalReserve)
class NaturalReserveAdmin(admin.ModelAdmin):
    """Administration des réserves naturelles"""
    list_display = ('name', 'area', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'area', 'description')
    ordering = ('name',)
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('reserve_id', 'name', 'type', 'area', 'description')
        }),
        ('Coordonnées', {
            'fields': ('coordinates',)
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(NationalPark)
class NationalParkAdmin(admin.ModelAdmin):
    """Administration des parcs nationaux"""
    list_display = ('name', 'area', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'area', 'description')
    ordering = ('name',)
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('park_id', 'name', 'type', 'area', 'description')
        }),
        ('Coordonnées', {
            'fields': ('coordinates',)
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(JWTBlacklistedToken)
class JWTBlacklistedTokenAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'token_type', 'blacklisted_at', 'expires_at', 'reason')
    list_filter = ('token_type', 'blacklisted_at', 'expires_at')
    search_fields = ('user_id', 'reason')
    ordering = ('-blacklisted_at',)
    readonly_fields = ('blacklisted_at',)
    
    fieldsets = (
        ('Informations du token', {
            'fields': ('token', 'token_type', 'user_id')
        }),
        ('Détails du blacklist', {
            'fields': ('blacklisted_at', 'expires_at', 'reason')
        }),
    )
    
    def has_add_permission(self, request):
        """Empêcher l'ajout manuel de tokens blacklistés"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Empêcher la modification des tokens blacklistés"""
        return False
