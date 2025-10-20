# serializers.py for courses app
# This file contains ModelSerializers for all models in courses/models.py

# serializers.py for courses app
# ModelSerializers for all models in courses/models.py
from rest_framework import serializers
from .models import Course, Module, Lesson, Enrollment, LessonCompletion, CourseReview, Resource

# Serializes Lesson model
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'module', 'title', 'description', 'lesson_type', 'article_content', 'video_url', 'attachment', 'is_preview', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'module', 'created_at', 'updated_at']

# Serializes Module model
class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True)
    class Meta:
        model = Module
        fields = ['id', 'course', 'title', 'description', 'is_active', 'created_at', 'updated_at', 'lessons']
        read_only_fields = ['id', 'course', 'created_at', 'updated_at']

# Serializes Course model
class CourseSerializer(serializers.ModelSerializer):
    # Example: expose computed property as read-only
    # progress = serializers.ReadOnlyField()
    modules = ModuleSerializer(many=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'mentor', 
                  'level', 'status', 'thumbnail', 'skills_covered', 
                  'price', 'students_count', 'is_free',
                  'published_at', 'duration_hours', 'created_at', 'updated_at', 'modules']
        read_only_fields = ['id', 'status', 'published_at', 'updated_at', 'created_at']



# Serializes Enrollment model
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'date_enrolled', 'is_active', 'payment_status', 'payment_date', 'certificate_issued', 'certificate_issued_at', 'enrolled_at', 'last_accessed']
        read_only_fields = ['id', 'date_enrolled', 'student', 'course', 'is_active', 'payment_status', 'payment_date', 'certificate_issued', 'certificate_issued_at', 'enrolled_at', 'last_accessed']

# Serializes LessonCompletion model
class LessonCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonCompletion
        fields = '__all__'
        read_only_fields = ['enrollment', 'lesson', 'completed_at', 'time_spent_minutes']

# Serializes CourseReview model
class CourseReviewSerializer(serializers.ModelSerializer):
    enrollment = EnrollmentSerializer(read_only=True)
    class Meta:
        model = CourseReview
        fields = ['id', 'rating', 'title', 'comment', 'created_at', 'updated_at', 'helpful_count', 'not_helpful_count', 'enrollment']
        read_only_fields = ['id', 'created_at', 'updated_at', 'enrollment', 'helpful_count', 'not_helpful_count']

# Serializes Resource model
class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'course', 'download_count', 'is_active', 'is_free']
