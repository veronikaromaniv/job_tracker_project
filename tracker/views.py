from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import JobApplication, Category, Event
from .forms import JobApplicationForm, EventForm
from django.utils import timezone
from datetime import timedelta


def home(request):
    return render(request, 'tracker/home.html')


@login_required
def dashboard(request):
    applications = JobApplication.objects.filter(owner=request.user)

    status_filter = request.GET.get('status', '')
    if status_filter == 'offer':
        applications = applications.filter(status__name__icontains='offer')
    elif status_filter == 'rejected':
        applications = applications.filter(status__name__icontains='reject')
    elif status_filter == 'interview':
        applications = applications.filter(status__name__icontains='interview')

    query = request.GET.get('q', '')
    if query:
        applications = applications.filter(
            Q(title__icontains=query) | Q(company__icontains=query)
        )

    SORT_FIELDS = {
        'created_at': 'created_at',
        'company': 'company',
        'title': 'title',
        'status': 'status__name',
    }
    sort = request.GET.get('sort', 'created_at')
    direction = request.GET.get('dir', 'desc')
    sort_field = SORT_FIELDS.get(sort, 'created_at')
    if direction == 'asc':
        applications = applications.order_by(sort_field)
    else:
        applications = applications.order_by(f'-{sort_field}')

    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    today = timezone.localdate()
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    upcoming_events = (
        Event.objects
        .filter(
            job__owner=request.user,
            date__gte=today_start,
            date__lt=today_start + timedelta(days=8),
        )
        .select_related('job')
        .order_by('date')[:5]
    )

    user_apps = JobApplication.objects.filter(owner=request.user)
    context = {
        'page_obj': page_obj,
        'offers_count': user_apps.filter(status__name__icontains='offer').count(),
        'rejected_count': user_apps.filter(status__name__icontains='reject').count(),
        'interview_count': user_apps.filter(status__name__icontains='interview').count(),
        'total_count': user_apps.count(),
        'query': query,
        'status_filter': status_filter,
        'sort': sort,
        'direction': direction,
        'upcoming_events': upcoming_events,
        'today': today,
    }
    return render(request, 'tracker/dashboard.html', context)


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
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
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


@login_required
def event_create(request, pk):
    job = get_object_or_404(JobApplication, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.job = job
            event.save()
            messages.success(request, "Подію додано!")
            return redirect('job_detail', pk=pk)
    else:
        form = EventForm()
    return render(request, 'tracker/event_form.html', {'form': form, 'job': job})


@login_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk, job__owner=request.user)
    job = event.job
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Подію оновлено!")
            return redirect('job_detail', pk=job.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'tracker/event_form.html', {'form': form, 'job': job, 'editing': True})


@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk, job__owner=request.user)
    job_pk = event.job.pk
    if request.method == 'POST':
        event.delete()
        messages.warning(request, "Подію видалено.")
        return redirect('job_detail', pk=job_pk)
    return render(request, 'tracker/event_confirm_delete.html', {'event': event})


@login_required
def calendar_view(request):
    return render(request, 'tracker/calendar.html')


@login_required
def api_events(request):
    events = Event.objects.filter(job__owner=request.user).select_related('job')

    event_type = request.GET.get('type')
    if event_type:
        events = events.filter(event_type=event_type)

    palette = {
        'interview': {'bg': 'rgba(234,88,12,0.10)', 'border': '#ea580c', 'text': '#c2410c'},
        'deadline':  {'bg': 'rgba(220,38,38,0.10)', 'border': '#dc2626', 'text': '#b91c1c'},
        'other':     {'bg': 'rgba(234,88,12,0.10)', 'border': '#ea580c', 'text': '#c2410c'},
    }

    events_data = [
        {
            'id': event.id,
            'title': event.title,
            'start': event.date.isoformat(),
            'url': reverse('job_detail', args=[event.job.id]),
            'backgroundColor': palette.get(event.event_type, palette['other'])['bg'],
            'borderColor':     palette.get(event.event_type, palette['other'])['border'],
            'textColor':       palette.get(event.event_type, palette['other'])['text'],
            'extendedProps': {
                'company':    event.job.company,
                'event_type': event.get_event_type_display(),
            },
        }
        for event in events
    ]

    return JsonResponse(events_data, safe=False)
