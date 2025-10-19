from rest_framework import permissions
from users.models import User

class IsMentor(permissions.BasePermission):
    def has_object_permissions(self, request, view, obj):
        print(view) 
        return request.user.role == User.MENTOR
    
class IsTalent(permissions.BasePermission):
    def has_object_permissions(self, request, view, obj):
        return request.user.role == User.TALENT

class IsStaff(permissions.BasePermission):
    def has_object_permissions(self, request, view, obj):
        return request.user.is_staff
    
