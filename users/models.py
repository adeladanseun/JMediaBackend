from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils import timezone

from skills.models import Skill

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
    
class User(AbstractBaseUser, PermissionsMixin):
    TALENT = 0
    CLIENT = 1
    MENTOR = 2
    ADMIN = 3
    ROLE_CHOICES = (
        (TALENT, 'Talent'),
        (CLIENT, 'Client'),
        (MENTOR, 'Mentor'),
        (ADMIN, 'Admin'),
    )
    username = None
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=40, blank=True, null=True)
    last_name = models.CharField(max_length=40, blank=True, null=True)

    role = models.IntegerField(choices=ROLE_CHOICES, default=TALENT)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, default='profile_pictures/default.png')
    phone_regex = RegexValidator(regex=r'^\+1?\d{9, 15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    skills = models.ManyToManyField(Skill, related_name='users')

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    website = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []#'first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def save(self, *args, **kwargs):
        if self.role==User.ADMIN:
            self.is_staff = True
        elif self.is_staff:
            self.role = User.ADMIN
        super().save(*args, **kwargs)
        
    def get_full_name(self):
        return f'{self.first_name or ""} {self.last_name or ""}'
    
    @property
    def is_talent(self):
        return self.role == User.TALENT
    
    @property
    def is_client(self):
        return self.role == User.CLIENT
    
    @property
    def is_mentor(self):
        return self.role == User.MENTOR
    
    @property
    def is_admin_user(self):
        return self.role == User.ADMIN or self.is_staff
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    title = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    bio = models.TextField(null=True, blank=True, max_length=500) 

    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_available = models.BooleanField(default=False)
    available_from = models.DateField(blank=True, null=True)

    notification_preferences = models.JSONField(default=dict, blank=True)

    completed_projects = models.PositiveIntegerField(default=0)
    success_rate = models.FloatField(default=0.0)

    def __str__(self):
        return f"Profile of {self.user.email}"




