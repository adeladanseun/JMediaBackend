from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from skills.models import Skill

# Create your models here.
class JobPosting(models.Model):
    FULL_TIME = 0
    PART_TIME = 1
    CONTRACT = 2
    FREELANCE = 3
    INTERNSHIP = 4

    JOB_TYPE = (
        (FULL_TIME, 'Full Time'),
        (PART_TIME, 'Part Time'),
        (CONTRACT, 'Contract'),
        (FREELANCE, 'Freelance'),
        (INTERNSHIP, 'Internship'),
    )

    ENTRY = 0
    MID = 1
    SENIOR = 2
    EXPERT = 3

    EXPERIENCE_LEVELS = (
        (ENTRY, 'Entry Level'),
        (MID, 'Mid Level'),
        (SENIOR, 'Senior'),
        (EXPERT, 'Expert'),
    )

    DRAFT = 0
    PUBLISHED = 1
    CLOSED = 2
    FILLED = 3

    STATUS = (
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
        (CLOSED, 'Closed'),
        (FILLED, 'Filled'),
    )

    FIXED = 0
    HOURLY = 1
    SALARY = 2
    MILESTONE = 3

    BUDGET_TYPE = (
        (FIXED, 'Fixed Price'),
        (HOURLY, 'Hourly Rate'),
        (SALARY, 'Monthly Salary'),
        (MILESTONE, 'Milestone Based'),
    )

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_postings', limit_choices_to={'role__in': [User.CLIENT, User.MENTOR, User.ADMIN]})
    title = models.CharField(max_length=200)
    description = models.TextField()
    job_type = models.IntegerField(choices=JOB_TYPE, default=FULL_TIME)
    experience_level = models.IntegerField(choices=EXPERIENCE_LEVELS, default=MID)
    required_skills = models.ManyToManyField(Skill, related_name='job_postings')

    location = models.CharField(max_length=200, blank=True, null=True, help_text="e.g., Remote, New York, NY.")

    is_remote = models.BooleanField(default=False)

    budget_type = models.IntegerField(choices=BUDGET_TYPE, default=FIXED)
    budget = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, validators=[MinValueValidator])
    duration_weeks = models.PositiveIntegerField(null=True, blank=True, help_text="Expected duration in weeks (for contracts)")

    application_deadline = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(choices=STATUS, default=DRAFT)

    #proposals_count = models.PositiveIntegerField(default=0)

    is_urgent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.status==self.__class__.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} by {self.client.get_full_name()}"
    
    @property
    def is_active(self):
        if self.status != self.__class__.PUBLISHED:
            return False
        if self.application_deadline and timezone.now() > self.application_deadline:
            return False
        return True
    
    @property
    def proposals_count(self):
        return self.proposals.count()

class Proposal(models.Model):
    SUBMITTED = 0
    UNDER_REVIEW = 1
    ACCEPTED = 2
    REJECTED = 3
    WITHDRAWN = 4

    STATUS = (
        (SUBMITTED, 'Submitted'),
        (UNDER_REVIEW, 'Under Review'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (WITHDRAWN, 'Withdrawn'),
    )

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='proposals')
    applier = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals', limit_choices_to={'role__in': [User.ADMIN, User.TALENT, User.MENTOR]})
    cover_letter = models.TextField()
    proposed_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    estimated_days = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="Estimated days to complete the project")
    
    attachment = models.FileField(upload_to='proposal_attachments/', blank=True, null=True, help_text="Resume, similar projects, proposed solution")

    status = models.IntegerField(choices=STATUS, default=SUBMITTED)

    client_notes = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Client rating of submitted proposal for future reference")

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['job', 'applier']
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Proposal by {self.applier.email} for {self.job.title}"
    
    @property
    def is_under_review(self):
        return self.status == self.__class__.UNDER_REVIEW
    
    @property
    def is_accepted(self):
        return self.status == self.__class__.ACCEPTED
    
    def accept(self):
        self.status = self.__class__.ACCEPTED
        self.save()

    def reject(self, note=None):
        self.status = self.__class__.REJECTED
        #can set client note here
        self.save()
    
    def withdraw(self):
        self.status = self.__class__.WITHDRAWN
        self.save()

class Contract(models.Model):
    """ Contract between clients and talents for accepted proposal. Remains even when jobposting and proposal is deleted due to its importance"""
    DRAFT = 0
    ACTIVE = 1
    COMPLETED = 2
    CANCELLED = 3
    DISPUTED = 4

    STATUS = (
        (DRAFT, 'Draft'),
        (ACTIVE, 'Active'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (DISPUTED, 'Disputed'),
    )
    job = models.OneToOneField(JobPosting, on_delete=models.SET_NULL, null=True, related_name='contract')
    proposal = models.OneToOneField(Proposal, on_delete=models.SET_NULL, null=True, related_name='contract')

    title = models.CharField(max_length=200, default='Contract', blank=True)
    description = models.TextField(blank=True, null=True)

    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_schedule = models.IntegerField()#flag

    status = models.IntegerField(choices=STATUS, default=DRAFT)
    progress = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    has_milestones = models.BooleanField(default=False)

    communication_channel = models.URLField(blank=True, help_text="Whatsapp, LinkedIn, Slack, Zoom or any other communication link")

    #can add client and talent review and rating here

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Contract: {self.title}"

    @property
    def is_active(self):
        return self.status == Contract.ACTIVE
    
    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date)
        return None
    
    def complete(self):
        self.status = Contract.COMPLETED
        self.completed_at = timezone.now()
        self.progress = 100.0
        self.save()

    def update_progress(self, progress):
        self.progress = max(0, min(100, progress))
        self.save()

class Milestone(models.Model):
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    APPROVED = 3
    PAID = 4

    STATUS = (
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (APPROVED, 'Approved'),
        (PAID, 'Paid'),
    )
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(blank=True, null=True)

    status = models.IntegerField(choices=STATUS, default=PAID)

    completed_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Milestone: {self.title} for {self.contract.title}"
    
    @property
    def is_overdue(self):
        if self.status in [Milestone.PENDING, Milestone.IN_PROGRESS]:
            if self.due_date:
                return self.due_date < timezone.now().date()
            else:
                if self.contract.end_date:
                    return self.contract.end_date < timezone.now().date()
        return False
    
    def complete(self):
        self.status = Milestone.COMPLETED
        self.completed_at = timezone.now()
        self.save()

    def approve(self):
        self.status = Milestone.APPROVED
        self.save()

    def mark_paid(self):
        self.status = Milestone.PAID
        self.paid_at = timezone.now()
        self.save()