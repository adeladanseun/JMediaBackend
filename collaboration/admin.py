from django.contrib import admin
from .models import Project, ProjectRole, ProjectMember, Task, ProjectFile, ProjectInvitation

# Register your models here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'project_lead', 'project_type', 'status', 'visibility', 'progress', 'created_at']
    list_filter = ['project_type', 'status', 'visibility', 'created_at']
    search_fields = ['title', 'description', 'created_by__email', 'project_lead__email']
    readonly_fields = ['progerss', 'created_at', 'updated_at']
    filter_horizontal = ['required_skills']

@admin.register(ProjectRole)
class ProjectRoleAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'can_manage_tasks', 'can_manage_members', 'can_edit_project', 'can_delete_project', 'max_members', 'is_active']
    list_filter = ['is_active', 'project']
    search_fields = ['title', 'project__title']
    readonly_fields = ['created_at']

@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'role', 'is_active', 'is_approved', 'joined_at']
    list_filter = ['is_active', 'is_approved', 'joined_at']
    search_fields = ['user__email', 'project__title']
    readonly_fields = ['joined_at', 'approved_at', 'left_at']

@admin.register(ProjectInvitation)
class ProjectInvitationAdmin(admin.ModelAdmin):
    list_display = ['invited_user', 'project', 'status', 'invited_by', 'expires_at', 'created_at']
    list_filter = ['status', 'expires_at', 'created_at']
    search_fields = ['invited_user__email', 'project__title', 'invited_by__user__email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'assigned_to', 'due_date', 'progress', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'project__title', 'assigned_to__user__email']
    readonly_fields = ['progress', 'created_at', 'updated_at']
    filter_horizontal = ['related_skills']
@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'project', 'category', 'uploaded_by', 'version', 'is_current', 'uploaded_at']
    list_filter = ['category', 'is_current', 'uploaded_at']
    search_fields = ['file_name', 'project__title', 'uploaded_by__user__email']
    readonly_fields = ['file_size', 'download_count', 'uploaded_at', 'updated_at']
