from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from datetime import datetime
from .models import User, UserProfile, PasswordResetToken, Drone, DroneFlight, CarouselImage, Airport, NaturalReserve, NationalPark, ProtectedAreaCoordinates


def validate_date_format(value):
    if value:
        try:
            if isinstance(value, str):
                datetime.strptime(value, '%Y-%m-%d')
            return value
        except ValueError:
            raise serializers.ValidationError("Le format de date doit être YYYY-MM-DD")
    return value


def validate_datetime_format(value):
    if value:
        try:
            if isinstance(value, str):
                datetime.fromisoformat(value.replace('Z', '+00:00'))
            return value
        except ValueError:
            raise serializers.ValidationError("Le format de date et heure doit être YYYY-MM-DDTHH:MM")
    return value


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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'birth_date', 'address', 'city', 'country', 'postal_code']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'phone', 'is_verified', 'created_at', 'profile']
        read_only_fields = ['id', 'is_verified', 'created_at']


class DroneSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    is_maintenance_due = serializers.ReadOnlyField()
    age_in_days = serializers.ReadOnlyField()
    
    class Meta:
        model = Drone
        fields = [
            'id', 'user', 'name', 'model', 'brand', 'drone_type', 'serial_number',
            'weight', 'max_payload', 'max_flight_time', 'max_range', 'max_altitude',
            'status', 'registration_number', 'insurance_info', 'maintenance_notes',
            'purchase_date', 'last_maintenance', 'next_maintenance', 'photo',
            'created_at', 'updated_at', 'is_maintenance_due', 'age_in_days'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'is_maintenance_due', 'age_in_days']


class DroneCreateSerializer(serializers.ModelSerializer):
    purchase_date = serializers.DateField(required=False, validators=[validate_date_format])
    last_maintenance = serializers.DateField(required=False, validators=[validate_date_format])
    next_maintenance = serializers.DateField(required=False, validators=[validate_date_format])
    
    class Meta:
        model = Drone
        fields = [
            'name', 'model', 'brand', 'drone_type', 'serial_number',
            'weight', 'max_payload', 'max_flight_time', 'max_range', 'max_altitude',
            'status', 'registration_number', 'insurance_info', 'maintenance_notes',
            'purchase_date', 'last_maintenance', 'next_maintenance', 'photo'
        ]
    
    def to_internal_value(self, data):
        if data:
            for date_field in ['purchase_date', 'last_maintenance', 'next_maintenance']:
                if date_field in data and data[date_field] == '':
                    data[date_field] = None
        return super().to_internal_value(data)


class DroneFlightSerializer(serializers.ModelSerializer):
    drone = DroneSerializer(read_only=True)
    pilot = UserSerializer(read_only=True)
    
    class Meta:
        model = DroneFlight
        fields = [
            'id', 'drone', 'pilot', 'flight_date', 'duration', 'location',
            'purpose', 'weather_conditions', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'drone', 'pilot', 'created_at']


class DroneFlightCreateSerializer(serializers.ModelSerializer):
    flight_date = serializers.DateTimeField(validators=[validate_datetime_format])
    
    class Meta:
        model = DroneFlight
        fields = [
            'drone', 'flight_date', 'duration', 'location',
            'purpose', 'weather_conditions', 'notes'
        ]
    
    def to_internal_value(self, data):
        if data:
            if 'flight_date' in data and data['flight_date'] == '':
                data['flight_date'] = None
        return super().to_internal_value(data)


class CarouselImageSerializer(serializers.ModelSerializer):
    image_url = serializers.ReadOnlyField()
    
    class Meta:
        model = CarouselImage
        fields = ['id', 'title', 'description', 'image', 'image_url', 'order', 'is_active', 'created_at']
        read_only_fields = ['id', 'image_url', 'created_at']


class CarouselImageListSerializer(serializers.ModelSerializer):
    image_url = serializers.ReadOnlyField()
    
    class Meta:
        model = CarouselImage
        fields = ['id', 'title', 'description', 'image_url', 'order', 'is_active']


class AirportSerializer(serializers.ModelSerializer):
    """Serializer pour l'API des aéroports et aérodromes"""
    coordinates = serializers.SerializerMethodField()
    type = serializers.CharField(source='airport_type')

    class Meta:
        model = Airport
        fields = [
            'id', 'airport_id', 'name', 'code', 'airport_type',
            'city', 'latitude', 'longitude', 'radius', 'description',
            'coordinates', 'type', 'is_active', 'created_by', 'created_at'
        ]

    def get_coordinates(self, obj):
        """Retourne les coordonnées au format [lat, lng] pour Leaflet"""
        return [float(obj.latitude), float(obj.longitude)]

    def to_representation(self, instance):
        """Personnalise la représentation pour la carte"""
        data = super().to_representation(instance)
        data['id'] = instance.airport_id
        return data


class AirportCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'aéroports et aérodromes"""
    
    class Meta:
        model = Airport
        fields = [
            'airport_id', 'name', 'code', 'airport_type',
            'city', 'latitude', 'longitude', 'radius', 'description'
        ]
    
    def create(self, validated_data):
        """Créer un aéroport avec l'utilisateur connecté"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ProtectedAreaCoordinatesSerializer(serializers.ModelSerializer):
    """Serializer pour les coordonnées des zones protégées"""
    
    class Meta:
        model = ProtectedAreaCoordinates
        fields = ['latitude', 'longitude', 'order', 'is_active']


class NaturalReserveSerializer(serializers.ModelSerializer):
    """Serializer pour les réserves naturelles"""
    
    coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = NaturalReserve
        fields = [
            'id', 'reserve_id', 'name', 'type', 'area', 
            'description', 'coordinates', 'is_active', 'created_by', 'created_at'
        ]
    
    def get_coordinates(self, obj):
        """Retourne les coordonnées au format [lat, lng] pour Leaflet"""
        return obj.formatted_coordinates


class NaturalReserveCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de réserves naturelles"""
    
    coordinates = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField(),
            min_length=2,
            max_length=2
        ),
        min_length=3,
        help_text="Liste des coordonnées [lat, lng] (minimum 3 points)"
    )
    
    class Meta:
        model = NaturalReserve
        fields = [
            'reserve_id', 'name', 'area', 'description', 'coordinates'
        ]
    
    def validate_coordinates(self, value):
        """Valider les coordonnées"""
        for coord in value:
            if len(coord) != 2:
                raise serializers.ValidationError("Chaque coordonnée doit avoir exactement 2 valeurs (lat, lng)")
            
            lat, lng = coord
            if not (-90 <= lat <= 90):
                raise serializers.ValidationError("La latitude doit être comprise entre -90 et 90")
            if not (-180 <= lng <= 180):
                raise serializers.ValidationError("La longitude doit être comprise entre -180 et 180")
        
        return value
    
    def create(self, validated_data):
        """Créer la réserve naturelle"""
        validated_data['type'] = 'natural_reserve'
        validated_data['is_active'] = False  # En attente d'approbation admin
        
        # Récupérer l'utilisateur depuis le contexte
        user = self.context.get('request').user if self.context.get('request') else None
        if user:
            validated_data['created_by'] = user
        
        # Les coordonnées sont déjà dans validated_data, pas besoin de les retirer
        reserve = NaturalReserve.objects.create(**validated_data)
        
        return reserve
    
    def to_representation(self, instance):
        """Personnalise la représentation pour la carte"""
        data = super().to_representation(instance)
        data['id'] = instance.reserve_id
        return data





class NationalParkSerializer(serializers.ModelSerializer):
    """Serializer pour les parcs nationaux"""
    
    coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = NationalPark
        fields = [
            'id', 'park_id', 'name', 'type', 'area', 
            'description', 'coordinates', 'is_active', 'created_by', 'created_at'
        ]
    
    def get_coordinates(self, obj):
        """Retourne les coordonnées au format [lat, lng] pour Leaflet"""
        return obj.formatted_coordinates


class NationalParkCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de parcs nationaux"""
    
    coordinates = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField(),
            min_length=2,
            max_length=2
        ),
        min_length=3,
        help_text="Liste des coordonnées [lat, lng] (minimum 3 points)"
    )
    
    class Meta:
        model = NationalPark
        fields = [
            'park_id', 'name', 'area', 'description', 'coordinates'
        ]
    
    def validate_coordinates(self, value):
        """Valider les coordonnées"""
        for coord in value:
            if len(coord) != 2:
                raise serializers.ValidationError("Chaque coordonnée doit avoir exactement 2 valeurs (lat, lng)")
            
            lat, lng = coord
            if not (-90 <= lat <= 90):
                raise serializers.ValidationError("La latitude doit être comprise entre -90 et 90")
            if not (-180 <= lng <= 180):
                raise serializers.ValidationError("La longitude doit être comprise entre -180 et 180")
        
        return value
    
    def create(self, validated_data):
        """Créer le parc national"""
        validated_data['type'] = 'national_park'
        validated_data['is_active'] = False  # En attente d'approbation admin
        
        # Récupérer l'utilisateur depuis le contexte
        user = self.context.get('request').user if self.context.get('request') else None
        if user:
            validated_data['created_by'] = user
        
        # Les coordonnées sont déjà dans validated_data, pas besoin de les retirer
        park = NationalPark.objects.create(**validated_data)
        
        return park
    
    def to_representation(self, instance):
        """Personnalise la représentation pour la carte"""
        data = super().to_representation(instance)
        data['id'] = instance.park_id
        return data



