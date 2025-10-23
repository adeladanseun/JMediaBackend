from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, UserProfile, PasswordResetCode

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
        
@receiver(pre_save, sender=PasswordResetCode)
def mark_old_code(sender, instance, **kwargs):
    sender.objects.filter(user=instance.user).update(is_used=True)
