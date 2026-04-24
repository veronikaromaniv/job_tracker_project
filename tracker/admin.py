from django.contrib import admin
from .models import Category, JobApplication, Event

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

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'job', 'event_type', 'date')
    list_filter = ('event_type', 'date')
    search_fields = ('title', 'job__title', 'job__company')
