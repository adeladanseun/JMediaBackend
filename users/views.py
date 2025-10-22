from django.shortcuts import render
from . import serializers
from . import models
from . import permissions
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

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_url = f"http://localhost:8000/users/password/reset/{uid}/{token}/"

            subject = "Password Reset Request"
            message = f"""
            Hello {user.email},

            You requested a password reset. Click the link below to reset your password:
            {reset_url}

            If you did not request this, please ignore this email.
            Regards,
            King J Media Team
            """
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                      recipient_list=[user.email], fail_silently=False)
            return Response({
                "details": "Check your email"
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = serializers.PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            uid = serializer.validated_data['uid']
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']

            try:
                user_id = force_str(urlsafe_base64_decode(uid))
                user = models.User.objects.get(pk=user_id)
                
                if default_token_generator.check_token(user, token):
                    user.set_password(new_password)
                    user.save()
                    return Response({
                        "details": "Password has been reset successfully."
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "details": "Invalid or expired token"
                    }, status=status.HTTP_400_BAD_REQUEST)
            except (TypeError, ValueError, OverflowError, models.User.DoesNotExist):
                return Response({
                    "details": "Invalid reset link"
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)