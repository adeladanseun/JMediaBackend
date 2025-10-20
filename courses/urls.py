from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
urlpatterns = [
    path('api/', views.api_root, name='course_api_root'), 
    path('api/course/', views.CourseListView.as_view(), name='api_course_list'),
    path('api/course/<int:pk>/', views.CourseDetailView.as_view(), name='api_course_detail'),
    path('api/module/', views.ModuleListView.as_view(), name='api_module_list'),
    path('api/lesson/', views.LessonListView.as_view(), name='api_lesson_list'),
    path('api/enrollment/', views.EnrollmentListView.as_view(), name='api_enrollment_list'),
    path('api/lessoncompletion/', views.LessonCompletionListView.as_view(), name='api_lesson_completion_list'),
    path('api/coursereview/', views.CourseReviewListView.as_view(), name='api_course_review_list'),
    path('api/resource/', views.ResourceListView.as_view(), name='api_resource_list'),
    
    
    
    #path('api/', include(router.urls)),
    #path('api-auth/', include('rest_framework.urls')),
]