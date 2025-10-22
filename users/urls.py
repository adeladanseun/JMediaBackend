from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('create/', views.UserCreateView.as_view(), name='user_creation'),
    path('signup/', views.UserCreateView.as_view(), name='user_signup'),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('password/reset/<str:uid>/<str:token>/', views.PasswordResetRequestView.as_view(), name='password_reset'),
]