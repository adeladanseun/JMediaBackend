from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Project
from users.models import User

@receiver(pre_delete, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    projects = Project.objects.filter(created_by=instance, visibility__in=[Project.PRIVATE, Project.INVITE_ONLY])
    if projects:
        projects.delete()