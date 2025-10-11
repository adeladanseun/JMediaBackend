from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def role_required(allowed_roles):
    """
    Decorator for views that checks the user's role 
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.role in allowed_roles or request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
                else:
                    raise PermissionDenied
            return redirect('login') #flag
        return _wrapped_view
    return decorator

def talent_required(view_func):
    return role_required(['talent'])(view_func)

def client_required(view_func):
    return role_required(['client'])(view_func)

def mentor_requied(view_func):
    return role_required(['mentor'])(view_func)

def admin_required(view_func):
    return role_required(['admin'])(view_func)

class RoleRequiredMixin:
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login') #flag
        
        if request.user.role not in self.allowed_roles and not request.user.is_superuser:
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs) #flag parent class inherits no parent and so i suspect super wont work