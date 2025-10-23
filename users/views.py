from django.shortcuts import render
from . import serializers
from . import models
from . import permissions
from . import emails
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics, status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

class UserCreateView(generics.CreateAPIView):
    """Creates a new user and requests a redirect to the login page

    Args:
        generics (CreateAPIView): generics.CreateAPIView
    """
    queryset = models.User.objects.all()
    serializer_class = serializers.UserCreateSerializer
    permission_classes = [permissions.IsNotAuthenticated]
    
    def perform_create(self, serializer):
        #do some stuff
        print('contacting email backend')
        serializer.save()
        
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = serializers.PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = models.User.objects.get(email=email)

            models.PasswordResetCode.objects.filter(user=user).update(is_used=True)#already taken care of in signals.py
            
            reset_code = models.PasswordResetCode.objects.create(user=user)

            subject = "Password Reset Request"
            context = {
                'subject': subject,
                'user': user,
                'reset_code': reset_code,
            }
            emails.EmailService.send_password_reset_email(context)
            
            return Response({
                "details": "Check your email"
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetVerifyView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = serializers.PasswordResetVerifySerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            reset_code = serializer.validated_data['reset_code']
            
            return Response ({
                "detail": "Verification code is valid",
                "email": user.email,
                "code": reset_code.code
            }, status=status.HTTP_200_OK
            )
        return Response(serializers.errors, status.HTTP_400_BAD_REQUEST)
    

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = serializers.PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            reset_code = serializer.validated_data['reset_code']
            new_password = serializer.validated_data['password1']

            user.set_password(new_password)
            user.save()
            
            reset_code.mark_used()
            
            models.PasswordResetCode.objects.filter(
                user=user,
                is_used=False,
            ).update(is_used=True)
            
            return Response(
                {"detail": "Password has been reset successfully."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class passwordChangeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = serializers.passwordChangeSerializer(
            data=request.data,
            context={
                'request': request,
            }
            )
        
        if serializer.is_valid():
            ##serializer already checks if the password is valid
            request.user.set_password(serializer.validated_data['password1'])
            return Response({
                "details": "Password change successful"
            })
        return Response({
            "details": "Error changing password"
        })
            
            
            
            