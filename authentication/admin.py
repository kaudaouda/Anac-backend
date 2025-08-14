from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, PasswordResetToken


class UserProfileInline(admin.StackedInline):
    """
    Inline pour le profil utilisateur
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ['avatar', 'bio', 'birth_date', 'address', 'city', 'country', 'postal_code']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Administration des utilisateurs
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
    Administration des profils utilisateurs
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
    Administration des tokens de réinitialisation
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
