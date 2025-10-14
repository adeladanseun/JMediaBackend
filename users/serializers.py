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
        read_only_fields = ['id', 'email']

# Serializes UserProfile model
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'is_available']
        read_only_fields = ['id']
