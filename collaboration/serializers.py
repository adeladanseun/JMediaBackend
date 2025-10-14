# serializers.py for collaboration app
# This file contains ModelSerializers for all models in collaboration/models.py
from rest_framework import serializers
from .models import Project, ProjectRole, ProjectMember, ProjectInvitation, Task, ProjectFile

# Serializes Project model
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'  # Serializes all fields

# Serializes ProjectRole model
class ProjectRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRole
        fields = '__all__'

# Serializes ProjectMember model
class ProjectMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMember
        fields = '__all__'

# Serializes ProjectInvitation model
class ProjectInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectInvitation
        fields = '__all__'

# Serializes Task model
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

# Serializes ProjectFile model
class ProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = '__all__'
