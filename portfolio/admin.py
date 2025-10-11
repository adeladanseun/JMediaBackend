from django.contrib import admin
from .models import PortfolioItem, PortfolioImage

# Register your models here.
@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'project_type', 'visibility', 'is_approved', 'is_featured', 'views_count', 'created_at']
    list_filter = ['project_type', 'visibility', 'is_approved', 'created_at']
    search_fields = ['title', 'description', 'owner__email', 'owner__first_name', 'owner__last_name']
    readonly_fields = ['views_count', 'likes_count', 'created_at', 'updated_at']
    filter_horizontal = ['skills_used']

@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ['portfolio_item', 'is_primary', 'uploaded_at']
    list_filter = ['is_primary', 'uploaded_at']
    search_fields = ['portfolio_item__title', 'caption']