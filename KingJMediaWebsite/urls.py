from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from courses import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


#router = routers.DefaultRouter()
#router.register('courses', views.CourseListView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('courses/', include('courses.urls')),
    #path('api/', include(router.urls)),
    
]
