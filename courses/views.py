from django.shortcuts import render
from .models import *
from .serializers import *
from users.permissions import *
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView


# Create your views here.
class CourseListView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser | IsMentor]
        return super().get_permissions()

@api_view(['GET'])
def api_root(request):
    return Response(
        {
            'message': 'Welcome to the API',
            'endpoints': {
                'course': '/api/course/',
                'module': '/api/module',
                'lesson': '/api/lesson',
                'enrollment': '/api/enrollment',
                'lesson_completion': '/api/lessoncompletion',
                'course_review': '/api/coursereview/',
                'resource': '/api/resource/'
            }
        }
    )
    
class ModuleListView(generics.ListAPIView):
    queryset  = Module.objects.all()
    serializer_class = ModuleSerializer
    
class LessonListView(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    
class EnrollmentListView(generics.ListAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    
class LessonCompletionListView(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonCompletionSerializer
    
class CourseReviewListView(generics.ListAPIView):
    queryset = CourseReview.objects.all()
    serializer_class = CourseReviewSerializer
    
class ResourceListView(generics.ListAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer