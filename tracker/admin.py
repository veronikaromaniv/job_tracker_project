from django.contrib import admin
from .models import Category, JobApplication

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    # Що ми бачимо в списку всіх вакансій
    list_display = ('title', 'company', 'status', 'owner', 'created_at')
    # Фільтри збоку
    list_filter = ('status', 'created_at')
    # Пошук
    search_fields = ('title', 'company')
