from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/ical/', views.export_ical, name='export_ical'),
]
