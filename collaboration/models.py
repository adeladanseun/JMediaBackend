from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from skills.models import Skill

# Create your models here.
class Project(models.Model):
    INTERNAL = 0
    CLIENT = 1
    LEARNING = 2
    OPEN_SOURCE = 3
    HACKATHON = 4

    PROJECT_TYPE = (
        (INTERNAL, 'Internal'),
        (CLIENT, 'Client'),
        (LEARNING, 'Learning'),
        (OPEN_SOURCE, 'Open Source'),
        (HACKATHON, 'Hackathon'),
    )

    PLANNING = 0
    ACTIVE = 1
    ON_HOLD = 2
    COMPLETED = 3
    CANCELLED = 4

    PROJECT_STATUS = (
        (PLANNING, 'Planning'),
        (ACTIVE, 'Active'),
        (ON_HOLD, 'On Hold'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    )

    PUBLIC = 0
    PRIVATE = 1
    INVITE_ONLY = 2

    VISIBILITY = (
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
        (INVITE_ONLY, 'Invite Only'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    
    project_type = models.IntegerField(choices=PROJECT_TYPE, default=INTERNAL)
    status = models.IntegerField(choices=PROJECT_STATUS, default=PLANNING)
    visibility = models.IntegerField(choices=VISIBILITY, default=PRIVATE)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='projects_created', null=True)
    project_lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='projects_led', limit_choices_to={'role__in': [User.TALENT, User.MENTOR, User.ADMIN]})
    required_skills = models.ManyToManyField(Skill, related_name='projects', blank=True)

    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)

    max_members = models.PositiveIntegerField(default=20, validators=[MinValueValidator(1), MaxValueValidator(50)])
    allow_requests = models.BooleanField(default=True, help_text="Allow members to request to join this project")

    repository_url = models.URLField(blank=True, null=True)
    project_url = models.URLField(blank=True, null=True)
    documentation_url = models.URLField(blank=True, null=True)

    progress = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    #task_count = models.PositiveIntegerField(default=0)
    #completed_task_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.project_lead:
            self.project_lead = self.created_by
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    @property
    def is_active(self):
        return self.status == self.__class__.ACTIVE
    
    @property
    def member_count(self):
        return self.members.filter(is_active=True).count() # type: ignore
    
    @property
    def has_vacancies(self):
        return self.member_count < self.max_members
    
    @property
    def days_remaining(self):
        if self.target_date and self.status == Project.ACTIVE:
            remaining = (self.target_date - timezone.now().date()).days
            return max(0, remaining)
        return None
    
    def update_progress(self):
        total_tasks = self.tasks.count() # type: ignore
        completed_tasks = self.tasks.filter(status=Task.COMPLETED).count() # type: ignore

        if total_tasks > 0:
            self.progress = (completed_tasks / total_tasks) * 100
            
            if self.progress >= 100 and self.status != Project.COMPLETED:
                self.status = Project.COMPLETED
                self.completed_date = timezone.now().date()
            self.save()
        return self.progress
    
    def can_user_join(self, user):
        if not self.allow_requests or self.member_count >= self.max_members or self.members.filter(user=user).exists(): # type: ignore
            return False
        return True
    
    def get_available_roles(self):
        return ProjectRole.objects.filter(project=self, is_active=True)
    
class ProjectRole(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='roles')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    can_manage_tasks = models.BooleanField(default=False)
    can_manage_members = models.BooleanField(default=False)
    can_edit_project = models.BooleanField(default=False)
    can_delete_content = models.BooleanField(default=False)

    max_members = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['project', 'title']

    def __str__(self):
        return f"{self.title} - {self.project.title}"
    
    @property
    def current_members(self):
        return self.members.filter(is_active=True).count() # type: ignore

    @property
    def has_vacancies(self):
        return self.current_members  < self.max_members
    
class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')#repetitive but above code already relies on its existence. Modify model methods to delete successfully
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.ForeignKey(ProjectRole, on_delete=models.SET_NULL, null=True, related_name='members')

    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)

    joined_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)

    member_notes = models.TextField(blank=True, help_text="Private notes about this member")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['project', 'user']

    def __str__(self):
        return f"{self.user.email} - {self.project.title}"
    
    def approve(self):
        if not self.is_approved:
            self.is_approved = True
            self.approved_at = timezone.now()
            self.save()
            
    def remove(self):
        self.delete() #instead, set is_active=False; left_at=timezone.now(); save()

    @property
    def completion_rate(self):
        assigned_tasks = self.tasks.filter(assigned_to=self) # pyright: ignore[reportAttributeAccessIssue]
        if assigned_tasks.count() > 0: # type: ignore
            completed_tasks = self.tasks.filter(assigned_to=self, status=Task.COMPLETED)
            return (completed_tasks.count() / assigned_tasks.count()) * 100  # type: ignore
        return 0
    
class ProjectInvitation(models.Model):
    PENDING = 0
    ACCEPTED = 1
    DECLINED = 2
    EXPIRED = 3

    STATUS = (
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined'),
        (EXPIRED, 'Expired'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invitations')
    invited_by = models.ForeignKey(ProjectMember, on_delete=models.CASCADE, related_name='sent_invitations')
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_invitations')
    role = models.ForeignKey(ProjectRole, on_delete=models.CASCADE, related_name='pending_invites')

    message = models.TextField(blank=True)
    status = models.IntegerField(choices=STATUS, default=PENDING) # type: ignore
    expires_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['project', 'invited_user']

    def accept(self):
        if (not self.expires_at) or (self.expires_at and (self.expires_at > timezone.now() and self.status == ProjectInvitation.PENDING)):
            member, created = ProjectMember.objects.get_or_create(project=self.project, user=self.invited_user, defaults={'role': self.role, 'is_approved': True, 'approved_at': timezone.now(), 'joined_at': timezone.now()})
            self.status = ProjectInvitation.ACCEPTED
            self.responded_at = timezone.now()
            self.save()

    def decline(self):
        if self.status == ProjectInvitation.PENDING:
            self.status = ProjectInvitation.DECLINED
            self.responded_at = timezone.now()
            self.save()

class Task(models.Model):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

    PRIORITY_LEVEL = (
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
        (CRITICAL, 'Critical'),
    )

    BACKLOG = 0
    TODO = 1
    IN_PROGRESS = 2
    REVIEW = 3
    COMPLETED = 4
    CANCELLED = 5

    STATUS = (
        (BACKLOG, 'Backlog'),
        (TODO, 'Todo'),
        (IN_PROGRESS, 'In Progress'),
        (REVIEW, 'Review'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    priority = models.IntegerField(choices=PRIORITY_LEVEL, default=MEDIUM)
    status = models.IntegerField(choices=STATUS, default=TODO)
    estimated_hours = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)], help_text="Estimated hours to complete")
    actual_hours = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)], help_text="Actual hours spent")

    assigned_to = models.ForeignKey(ProjectMember, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(ProjectMember, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    
    due_date = models.DateField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    related_skills = models.ManyToManyField(Skill, related_name='tasks')
    
    progress = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['priority', 'due_date']

    def __str__(self):
        return f"{self.title} - {self.project.title}"
    
    @property
    def is_overdue(self):
        return (self.due_date and self.due_date < timezone.now().date() and self.status not in [Task.COMPLETED, Task.CANCELLED])
    
    @property
    def has_subtasks(self):
        return self.subtasks.exists() # type: ignore
    
    def start_task(self):
        if self.status == Task.TODO:
            self.status = Task.IN_PROGRESS
            self.started_at = timezone.now()
            self.save()

    def complete_task(self):
        if self.status != Task.COMPLETED:
            self.status = Task.COMPLETED
            self.progress = 100.0
            self.completed_at = timezone.now()
            self.save()
            self.project.update_progress()

    def update_progress(self, progress):
        progress = max(0, min(100, progress))
        self.progress = progress
        if progress == 100:
            self.complete_task()
        elif progress > 0 and self.status == Task.TODO:
            self.status = Task.IN_PROGRESS
        self.save()

class ProjectFile(models.Model):
    DOCUMENT = 0
    DESIGN = 1
    CODE = 2
    IMAGE = 3
    VIDEO = 4
    AUDIO = 5
    OTHER = 6

    FILE_CATEGORIES = (
        (DOCUMENT, 'Document'),
        (DESIGN, 'Design'),
        (CODE, 'Code'),
        (IMAGE, 'Image'),
        (VIDEO, 'Video'),
        (AUDIO, 'Audio'),
        (OTHER, 'Other'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    uploaded_by = models.ForeignKey(ProjectMember, on_delete=models.SET_NULL, null=True, related_name='uploaded_files')

    file = models.FileField(upload_to='project_files/')
    description = models.TextField(blank=True, null=True)
    category = models.IntegerField(choices=FILE_CATEGORIES, default=DOCUMENT)
    is_current = models.BooleanField(default=False)
    version = models.IntegerField(default=1)
    parent_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='child_versions')
    is_public = models.BooleanField(default=False, help_text="Visible to all project members")

    download_count = models.PositiveIntegerField(default=0)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.file.name} - {self.project.title}"
    
    @property
    def file_name(self):
        if self.file:
            return self.file.name
        return 'NO_FILE'
    
    @property
    def file_size(self):
        if self.file:
            return self.file.size
        return 0
    def increment_download_count(self):
        self.download_count += 1
        self.save()

    def create_new_version(self, new_file, description=None):
        self.is_current = False
        self.save()

        new_version = self.__class__.objects.create(
            project=self.project,
            uploaded_by=self.uploaded_by,
            file=new_file,
            description=description or self.description,
            category=self.category,
            version=self.version + 1,
            is_current=True,
            parent_version=self
        )
        return new_version