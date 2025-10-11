from django.contrib import admin
from .models import Course, Module, Lesson, Enrollment, CourseReview, Resource

# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'mentor', 'level', 'price', 'status', 'students_count', 'average_rating', 'created_at']
    list_filter = ['status', 'level', 'is_free', 'is_featured', 'category', 'created_at']
    search_fields = ['title', 'description', 'mentor__email', 'mentor__first_name', 'mentor__last_name']
    readonly_fields = ['students_count', 'average_rating', 'review_count', 'created_at', 'updated_at']
    prepopulated_fields = {'title': ['title']}
    filter_horizontal = ['skills_covered']

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'is_active', 'created_at']
    list_filter = ['course', 'is_active']
    search_fields = ['title', 'course__title']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'lesson_type', 'order', 'is_preview', 'is_active']
    list_filter = ['lesson_type', 'is_preview', 'is_active', 'module__course']
    search_fields = ['title', 'module__title', 'module__course__title']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'payment_status', 'progress', 'enrolled_at']
    list_filter = ['payment_status', 'is_active', 'enrolled_at']
    search_fields = ['student__email', 'course__title']
    readonly_fields = ['enrolled_at', 'last_accessed']

@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['enrollment__student__email', 'enrollment__course__title', 'title']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'is_free', 'download_count', 'created_at']
    list_filter = ['resource_type', 'is_free', 'is_active']
    search_fields = ['title', 'description']
    readonly_fields = ['download_count', 'file_size', 'created_at', 'updated_at']