from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from skills.models import Skill

# Create your models here.

class PortfolioItem(models.Model):
    WEB = 0
    MOBILE = 1
    DESIGN = 2
    MARKETING = 3
    VIDEO = 4
    WRITING = 5
    OTHER = 6
    
    PROJECT_TYPES = (
        (WEB, 'Web Development'),
        (MOBILE, 'Mobile App'),
        (DESIGN, 'UI/UX Design'),
        (MARKETING, 'Digital Marketing'),
        (VIDEO, 'Video Production'),
        (WRITING, 'Writing'),
        (OTHER, 'Other'),
    )


    COMPLETED = 0
    IN_PROGRESS = 1
    NOT_STARTED = 2

    PROJECT_STATUS = (
        (COMPLETED, 'Completed'),
        (IN_PROGRESS, 'In Progress'),
        (NOT_STARTED, 'Not Started'),
    )

    PUBLIC = 0
    PRIVATE = 1
    LINK_ONLY = 2
    
    VISIBILITY = (
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
        (LINK_ONLY, 'Link Only'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, 
                            related_name='portfolio_items', 
                            limit_choices_to={'role__in': [User.TALENT, User.MENTOR, User.ADMIN]})
    title = models.CharField(max_length=200)
    description = models.TextField()

    project_type = models.IntegerField(choices=PROJECT_TYPES, default=OTHER)
    project_status = models.IntegerField(choices=PROJECT_STATUS, default=IN_PROGRESS)
    visibility = models.IntegerField(choices=VISIBILITY, default=PUBLIC)

    skills_used = models.ManyToManyField(Skill, related_name='portfolio_items', blank=True)
    technologies = models.CharField(max_length=500, blank=True, null=True, help_text="Comma-separated list of technologies used")

    client_name = models.CharField(max_length=200, blank=True, help_text="Leave blank or put your name if it belongs to you or client is private")
    project_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True, help_text="Can link other git based related storage link")

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)

    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.owner.get_full_name()}"
    
    @property
    def is_visible(self):
        return self.visibility in [PortfolioItem.PUBLIC, PortfolioItem.LINK_ONLY]
    
    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])

class PortfolioImage(models.Model):
    portfolio_item = models.ForeignKey(PortfolioItem, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='portfolio_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.portfolio_item.title}"
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            self.__class__.objects.filter(
                portfolio_item=self.portfolio_item, is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)


