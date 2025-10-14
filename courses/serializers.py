# serializers.py for courses app
# This file contains ModelSerializers for all models in courses/models.py

# serializers.py for courses app
# ModelSerializers for all models in courses/models.py
from rest_framework import serializers
from .models import Course, Module, Lesson, Enrollment, LessonCompletion, CourseReview, Resource

# Serializes Course model
class CourseSerializer(serializers.ModelSerializer):
    # Example: expose computed property as read-only
    # progress = serializers.ReadOnlyField()
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'mentor', 'level', 'status', 'thumbnail']
        read_only_fields = ['id', 'status']

# Serializes Module model
class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'

# Serializes Lesson model
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

# Serializes Enrollment model
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'course', 'date_enrolled', 'is_active']
        read_only_fields = ['id', 'date_enrolled']

# Serializes LessonCompletion model
class LessonCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonCompletion
        fields = '__all__'

# Serializes CourseReview model
class CourseReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseReview
        fields = ['id', 'course', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

# Serializes Resource model
class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'
