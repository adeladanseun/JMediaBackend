from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from skills.models import Skill, Category

# Create your models here.
class Course(models.Model):
    """ Main course model for the learning portal """
    BEGINNER = 0
    INTERMEDIATE = 1
    ADVANCED = 2

    LEVEL_CHOICES = (
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
    )

    DRAFT = 0
    PUBLISHED = 1
    ARCHIVED = 2

    STATUS_CHOICES = (
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
        (ARCHIVED, 'Archived'),
    )

    title = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)#
    short_description = models.CharField(max_length=300) 

    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_created', limit_choices_to={'role__in': [User.MENTOR, User.ADMIN]})
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    skills_covered = models.ManyToManyField(Skill, related_name='courses')
    thumbnail = models.ImageField(upload_to='courses_thumbnails/', null=True, blank=True, help_text='Recommended pixel dimension ...')
    preview_video = models.URLField(null=True, blank=True, help_text="YouTube URL for course preview")
    level = models.IntegerField(choices=LEVEL_CHOICES, default=BEGINNER)
    duration_hours = models.FloatField(default=0.0, help_text="Total course duration in hours")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    is_free = models.BooleanField(default=False)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    status = models.IntegerField(choices=STATUS_CHOICES, default=DRAFT)
    students_count = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    review_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_certified = models.BooleanField(default=False, help_text="Course offers certification")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.status == Course.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        if self.is_free:
            self.price = 0.00
            self.discount_price = None

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price
    
    @property
    def is_on_discount(self):
        return self.discount_price is not None and self.discount_price < self.price #flag is not None might be a problem
    
    @property
    def discount_percentage(self):
        if self.is_on_discount:
            return int((( self.price - self.discount_price ) / self.price ) * 100 )
        return 0
    
    #@property
    def update_rating(self):
        reviews = self.enrollments.review.filter(is_approved=True) #flag might need to get all enrollments and iterate through each review for the rating to sum up
        if reviews.exists():
            self.average_rating = sum([review.rating for review in reviews]) / reviews.count()
            self.review_count = reviews.count()
            self.save()
    
    #property
    def get_total_lessons(self):
        return sum([module.lessons.count() for module in self.modules.all()])
    
    #property
    def get_total_duration(self):
        total_minutes = sum([sum([lesson.duration_minutes for lesson in module.lessons.all()]) for module in self.modules.all()])
        return total_minutes
    
class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        #unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def get_lessons_count(self):
        return self.lessons.count()
    
class Lesson(models.Model):
    VIDEO = 0
    ARTICLE = 1
    QUIZ = 2
    ASSIGNMENT = 3

    LESSON_TYPES = (
        (VIDEO, 'Video'),
        (ARTICLE, 'Article'),
        (QUIZ, 'Quiz'),
        (ASSIGNMENT, 'Assignment'),
    )

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    lesson_type = models.IntegerField(choices=LESSON_TYPES, default=ARTICLE)

    video_url = models.URLField(blank=True, null=True, help_text="YouTube or direct video URL")
    article_content = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='lesson_attachments/', blank=True, null=True, help_text='PDF, PowerPoint or other resources')
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Lesson duration in minutes")
    order = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False, help_text="Mark if this lesson can be previewed without enrollment")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        #unique_together = ['module', 'order']

    def __str__(self):
        return f"C({self.module.course.title}) - M({self.module.title}) - L({self.title})"
    
    @property
    def course(self):
        return self.module.course
    
class Enrollment(models.Model):
    PENDING = 0
    COMPLETED = 1
    FAILED = 2
    REFUNDED = 3

    PAY_STAT = (
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (REFUNDED, 'Refunded'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', limit_choices_to={'role__in': [User.TALENT, User.ADMIN]})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')

    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.IntegerField(choices=PAY_STAT, default=PENDING)
    payment_date = models.DateTimeField(null=True, blank=True)

    progress = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="Course completion percentage")
    completed_at = models.DateTimeField(null=True, blank=True)

    certificate_issued = models.BooleanField(default=False)
    certificate_issued_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course')


    def __str__(self):
        return f"{self.student.email} - {self.course.title}"
    
    def update_progress(self):
        total_lessons = self.course.get_total_lessons()
        if total_lessons > 0:
            completed_lessons = self.lesson_completions.count()
            self.progress = (completed_lessons / total_lessons) * 100

            if self.progress >= 100 and not self.completed_at: #if course is completed by the student
                self.completed_at = timezone.now()
                if self.course.is_certified:#if the course offers certification
                    self.certificate_issued = True
                    self.certificate_issued_at = timezone.now
            self.save()

    @property
    def is_completed(self):
        return self.progress >= 100

    @property
    def time_since_enrollment(self):
        return timezone.now() - self.enrolled_at
    
class LessonCompletion(models.Model):
    """ Tracks completion of individual lesson in a module """
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_completions')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='completions')

    completed_at = models.DateTimeField(auto_now_add=True)
    time_spent_minutes = models.PositiveIntegerField(default=0, help_text="Time Spent on lesson in minutes")
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('enrollment', 'lesson')

    def __str__(self):
        return f"{self.enrollment.student.email} completed {self.lesson.title}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.enrollment.update_progress()

class CourseReview(models.Model):
    """Student review and rating for courses"""
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Rating from 1 to 5 stars")
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(null=True, blank=True)

    is_approved = models.BooleanField(default=False)

    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.enrollment.course.title} by {self.enrollment.student.email}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.is_approved:
            self.enrollment.course.update_rating()

class Resource(models.Model):
    TEMPLATE = 0
    EBOOK = 1
    CHEATSHEET = 2
    CODE = 3
    TOOL = 4
    OTHER = 5

    RESOURCE_TYPE = (
        (TEMPLATE, 'Template'),
        (EBOOK, 'E-book'),
        (CHEATSHEET, 'Cheat Sheet'),
        (CODE, 'Source Code'),
        (TOOL, 'Tool'),
        (OTHER, 'Other'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    resource_type = models.IntegerField(choices=RESOURCE_TYPE, default=OTHER)

    file = models.FileField(upload_to='course_resources/')
    file_size = models.PositiveIntegerField(editable=False, blank=True, null=True)

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources', null=True, blank=True)
    is_free = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def increment_download_count(self):
        self.download_count += 1
        self.save()