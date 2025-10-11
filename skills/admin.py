from django.contrib import admin
from .models import Skill, SkillCategory, Category

# Register your models here.
admin.site.register(Skill)
admin.site.register(SkillCategory) 

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    list_filter = ('parent',)
    search_fields = ('name', 'description')