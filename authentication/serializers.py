from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, PasswordResetToken


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'password', 'confirm_password', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Les mots de passe ne correspondent pas."})
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Un utilisateur avec cet email existe déjà."})
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        # Utiliser la méthode create_user de notre UserManager personnalisé
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            
            if not user:
                raise serializers.ValidationError("Impossible de se connecter avec les identifiants fournis.")
            
            if not user.is_active:
                raise serializers.ValidationError("Ce compte utilisateur a été désactivé.")
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("Les champs email et mot de passe sont requis.")


class UserDetailSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'is_verified', 'created_at', 'updated_at', 'profile']
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']
    
    def get_profile(self, obj):
        if hasattr(obj, 'profile'):
            return {
                'avatar': obj.profile.avatar.url if obj.profile.avatar else None,
                'bio': obj.profile.bio,
                'city': obj.profile.city,
                'country': obj.profile.country
            }
        return None


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, validators=[validate_password], style={'input_type': 'password'})
    confirm_new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "Les nouveaux mots de passe ne correspondent pas."})
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("Aucun utilisateur actif trouvé avec cet email.")
        return value
