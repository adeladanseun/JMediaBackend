# serializers.py for users app
# This file contains ModelSerializers for all models in users/models.py

# serializers.py for users app
# ModelSerializers for all models in users/models.py
from rest_framework import serializers
from .models import User, UserProfile

# Serializes User model
class UserSerializer(serializers.ModelSerializer):
    # Example: expose email as read-only
    email = serializers.ReadOnlyField()
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active']
        read_only_fields = ['id', 'email', 'is_active']
        
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 'role']
        read_only_fields = ['is_active']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        # The `password2` field is not part of the model, so we remove it
        # before calling the `create_user` method.
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
    
        
# Serializes UserProfile model
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'is_available']
        read_only_fields = ['id']

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try: 
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    uid = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        try:
            self.validate_password(attrs['new_password'])
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        return attrs