from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import JobApplication, Category
from .forms import JobApplicationForm
from django.utils import timezone

def home(request):
    return render(request, 'tracker/home.html')

@login_required
def dashboard(request):
    applications = JobApplication.objects.filter(owner=request.user)

    # Фільтр по статусу
    status_filter = request.GET.get('status', '')
    if status_filter == 'offer':
        applications = applications.filter(status__name='Offer')
    elif status_filter == 'rejected':
        applications = applications.filter(status__name='Rejected')
    elif status_filter == 'interview':
        applications = applications.filter(status__name='Interview')

    # Пошук
    query = request.GET.get('q', '')
    if query:
        all_apps = list(applications)
        query_lower = query.lower()
        applications = [
            app for app in all_apps
            if query_lower in app.title.lower() or query_lower in app.company.lower()
        ]

    # Пагінація
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'offers_count': JobApplication.objects.filter(owner=request.user, status__name='Offer').count(),
        'rejected_count': JobApplication.objects.filter(owner=request.user, status__name='Rejected').count(),
        'interview_count': JobApplication.objects.filter(owner=request.user, status__name='Interview').count(),
        'total_count': JobApplication.objects.filter(owner=request.user).count(),
        'query': query,
        'status_filter': status_filter,
    }
    return render(request, 'tracker/dashboard.html', context)

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Акаунт створено! Ласкаво просимо!")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def job_create(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.owner = request.user
            job.save()
            messages.success(request, "Вакансію успішно додано!")
            return redirect('dashboard')
    else:
        form = JobApplicationForm()
    return render(request, 'tracker/job_form.html', {'form': form, 'title': 'Додати вакансію'})

@login_required
def job_detail(request, pk):
    job = get_object_or_404(JobApplication, pk=pk, owner=request.user)
    return render(request, 'tracker/job_detail.html', {'job': job})

@login_required
def job_edit(request, pk):
    job = get_object_or_404(JobApplication, pk=pk, owner=request.user)
    old_status = job.status  # запам'ятовуємо старий статус
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, instance=job)
        if form.is_valid():
            new_job = form.save(commit=False)
            if old_status != new_job.status:  # статус змінився?
                from django.utils import timezone
                new_job.status_changed_at = timezone.now()
            new_job.save()
            messages.success(request, "Зміни збережено!")
            return redirect('dashboard')
    else:
        form = JobApplicationForm(instance=job)
    return render(request, 'tracker/job_form.html', {'form': form, 'title': 'Редагувати вакансію'})

@login_required
def job_delete(request, pk):
    job = get_object_or_404(JobApplication, pk=pk, owner=request.user)
    if request.method == 'POST':
        job.delete()
        messages.warning(request, "Вакансію видалено.")
        return redirect('dashboard')
    return render(request, 'tracker/job_confirm_delete.html', {'job': job})