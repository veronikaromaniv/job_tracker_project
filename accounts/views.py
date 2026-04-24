import csv
import datetime

from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from tracker.models import Event, JobApplication


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Акаунт створено! Ласкаво просимо!")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    pw_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_info':
            request.user.first_name = request.POST.get('first_name', '').strip()
            request.user.last_name  = request.POST.get('last_name', '').strip()
            request.user.email      = request.POST.get('email', '').strip()
            request.user.save()
            messages.success(request, "Дані профілю оновлено!")
            return redirect('profile')

        elif action == 'change_password':
            pw_form = PasswordChangeForm(user=request.user, data=request.POST)
            if pw_form.is_valid():
                pw_form.save()
                update_session_auth_hash(request, pw_form.user)
                messages.success(request, "Пароль успішно змінено!")
                return redirect('profile')

    return render(request, 'accounts/profile.html', {'pw_form': pw_form})


@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="job_applications.csv"'
    response.write('﻿')

    writer = csv.writer(response)
    writer.writerow(['Посада', 'Компанія', 'Статус', 'Посилання', 'Нотатки', 'Дата додавання', 'Статус змінено'])

    applications = (
        JobApplication.objects
        .filter(owner=request.user)
        .select_related('status')
        .order_by('-created_at')
    )
    for app in applications:
        writer.writerow([
            app.title,
            app.company,
            app.status.name if app.status else '',
            app.url,
            app.description,
            app.created_at.strftime('%d.%m.%Y'),
            app.status_changed_at.strftime('%d.%m.%Y') if app.status_changed_at else '',
        ])

    return response


@login_required
def export_ical(request):
    events = Event.objects.filter(job__owner=request.user).select_related('job')

    ical_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//JobTracker//Calendar//UK",
        "CALSCALE:GREGORIAN",
    ]

    for event in events:
        utc = datetime.timezone.utc
        start_time = event.date.astimezone(utc).strftime("%Y%m%dT%H%M%SZ")
        end_time = (event.date + datetime.timedelta(hours=1)).astimezone(utc).strftime("%Y%m%dT%H%M%SZ")
        job_url = reverse('job_detail', args=[event.job.id])

        ical_content.extend([
            "BEGIN:VEVENT",
            f"UID:event-{event.id}@jobtracker",
            f"DTSTAMP:{datetime.datetime.now(utc).strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{start_time}",
            f"DTEND:{end_time}",
            f"SUMMARY:{event.title} - {event.job.company}",
            f"DESCRIPTION:Подія для вакансії {event.job.title} у компанії {event.job.company}\\nПосилання: {job_url}",
            "END:VEVENT",
        ])

    ical_content.append("END:VCALENDAR")

    response = HttpResponse("\r\n".join(ical_content), content_type="text/calendar")
    response['Content-Disposition'] = 'attachment; filename="job_tracker_calendar.ics"'
    return response
