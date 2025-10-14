# serializers.py for skills app
# This file contains ModelSerializers for all models in skills/models.py

# serializers.py for skills app
# ModelSerializers for all models in skills/models.py
from rest_framework import serializers
from .models import Category, SkillCategory, Skill

# Serializes Category model
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

# Serializes SkillCategory model
class SkillCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillCategory
        fields = '__all__'

# Serializes Skill model
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'description']
        read_only_fields = ['id']
