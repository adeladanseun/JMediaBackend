# serializers.py for users app
# This file contains ModelSerializers for all models in users/models.py

# serializers.py for users app
# ModelSerializers for all models in users/models.py

from rest_framework import serializers
from .models import User, UserProfile, PasswordResetCode
from django.conf import settings

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
    role_name = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 'role', 'role_name']
        read_only_fields = ['is_active']
    
    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({
                "details": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        # The `password2` field is not part of the model, so we remove it
        # before calling the `create_user` method.
        validated_data.pop("password2")
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
            raise serializers.ValidationError({
                "details": "User with this email does not exist."
            })
        return value

class PasswordResetVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=settings.RESET_CODE_LENGTH, write_only=True)
    
    def validate(self, data):
        email = data['email']
        code = data['code']
        
        try:
            user = User.objects.get(email=email)
            reset_code = PasswordResetCode.objects.filter(
                user=user,
                code=code,
                is_used=False
            ).latest('created_at')
            
            if not reset_code.is_valid:
                raise serializers.ValidationError({
                    "details": "Invalid or expired code"
                })

            data['user'] = user
            data['reset_code'] = reset_code
            
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "details": "No user found with this email"
            })
        except PasswordResetCode.DoesNotExist:
            raise serializers.ValidationError({
                "details": "Invalid verification code"
            })
        
        return data
    
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=settings.RESET_CODE_LENGTH)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    def validate(self, attrs):
        
        email = attrs['email']
        code = attrs['code']
        
        try:
            user = User.objects.get(email=email)
            reset_code = PasswordResetCode.objects.filter(
                user=user,
                code=code,
                is_used=False
            ).latest('created_at')
            
            if not reset_code.is_valid:
                raise serializers.ValidationError({
                    "details": "Invalid or expired code"
                    })
            
            attrs['user'] = user
            attrs['reset_code'] = reset_code
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "details": "No user found with this email address."
                })
        except PasswordResetCode.DoesNotExist:
            raise serializers.ValidationError({
                "details": "Invalid verification code."
                })
        
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({
                "details": "Passwords do not match."
                })
        if len(attrs['password1']) <= settings.PASSWORD_MIN_LENGTH:
            raise serializers.ValidationError({
                "details": "Password should be longer than 5 characters"
                })
        return attrs
    
class passwordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({
                "details": "Password is incorrect"
            })
        return value
    
    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({
                "details": "Passwords do not match"
            })
        
        try:
            self.validate_old_password(data['password'])
        except serializers.ValidationError as e:
            raise serializers.ValidationError({
                "details": "Passwords do not match"
            })

        return data
    
    
    