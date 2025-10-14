# serializers.py for marketplace app
# This file contains ModelSerializers for all models in marketplace/models.py

# serializers.py for marketplace app
# ModelSerializers for all models in marketplace/models.py
from rest_framework import serializers
from .models import JobPosting, Proposal, Contract, Milestone

# Serializes JobPosting model
class JobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = ['id', 'title', 'description', 'posted_by', 'created_at', 'status']
        read_only_fields = ['id', 'created_at']

# Serializes Proposal model
class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = '__all__'

# Serializes Contract model
class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ['id', 'proposal', 'start_date', 'end_date', 'status']
        read_only_fields = ['id', 'start_date']

# Serializes Milestone model
class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = '__all__'
