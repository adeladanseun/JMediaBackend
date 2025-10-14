# serializers.py for portfolio app
# This file contains ModelSerializers for all models in portfolio/models.py

# serializers.py for portfolio app
# ModelSerializers for all models in portfolio/models.py
from rest_framework import serializers
from .models import PortfolioItem, PortfolioImage

# Serializes PortfolioItem model
class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = ['id', 'title', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

# Serializes PortfolioImage model
class PortfolioImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioImage
        fields = '__all__'
