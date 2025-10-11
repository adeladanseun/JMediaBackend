from django.contrib import admin
from .models import JobPosting, Proposal, Contract, Milestone

# Register your models here.
@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'job_type', 'status', 'budget', 'proposals_count', 'created_at']
    list_filter = ['job_type', 'status', 'is_urgent', 'created_at']
    search_fields = ['title', 'description', 'client__email', 'client__first_name', 'client__last_name']
    readonly_fields = ['proposals_count', 'created_at', 'updated_at']
    filter_horizontal = ['required_skills']

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ['job', 'applier', 'status', 'proposed_amount', 'submitted_at']
    list_filter = ['status', 'submitted_at']
    search_fields = ['job__title', 'applier__email', 'cover_letter']
    readonly_fields = ['submitted_at', 'updated_at']

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['title', 'job', 'status', 'total_amount', 'progress', 'created_at']
    list_filter = ['status', 'payment_schedule', 'created_at']
    search_fields = ['title', 'description', 'job__title']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['title', 'contract', 'amount', 'due_date', 'status']
    list_filter = ['status', 'due_date']
    search_fields = ['title', 'contract__title']