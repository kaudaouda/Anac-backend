from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, PasswordResetToken, Drone, DroneFlight, CarouselImage


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
    list_display = ['email', 'full_name', 'phone', 'is_verified', 'is_active', 'is_staff', 'created_at']
    list_filter = ['is_verified', 'is_active', 'is_staff', 'created_at', 'groups']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Statut', {'fields': ('is_verified', 'last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 'password1', 'password2'),
        }),
    )
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Nom complet'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Administration of user profiles
    """
    list_display = ['user_email', 'user_full_name', 'city', 'country', 'has_avatar']
    list_filter = ['city', 'country', 'birth_date']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'city', 'country']
    readonly_fields = ['user']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    
    def user_full_name(self, obj):
        return obj.user.full_name
    user_full_name.short_description = 'Nom complet'
    
    def has_avatar(self, obj):
        if obj.avatar:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_avatar.short_description = 'Avatar'


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Administration of password reset tokens
    """
    list_display = ['user_email', 'token_preview', 'created_at', 'expires_at', 'is_used', 'is_expired']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['user', 'token', 'created_at', 'expires_at']
    
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
    list_display = ['name', 'user_full_name', 'user_email', 'drone_type', 'status', 'is_maintenance_due', 'created_at']
    list_filter = ['drone_type', 'status', 'created_at', 'purchase_date']
    search_fields = ['name', 'model', 'brand', 'serial_number', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'user', 'created_at', 'updated_at', 'is_maintenance_due', 'age_in_days']
    ordering = ['-created_at']
    
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
    list_display = ['drone_name', 'pilot_full_name', 'flight_date', 'duration', 'location', 'purpose']
    list_filter = ['flight_date', 'drone__drone_type', 'drone__user']
    search_fields = ['drone__name', 'pilot__email', 'pilot__first_name', 'pilot__last_name', 'location', 'purpose']
    readonly_fields = ['id', 'drone', 'pilot', 'created_at']
    ordering = ['-flight_date']
    
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
    list_display = ['title', 'order', 'is_active', 'image_preview', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'created_at']
    
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
