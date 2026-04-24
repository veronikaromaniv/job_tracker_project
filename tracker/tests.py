from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from .models import Category, JobApplication, Event


class JobApplicationModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.status_applied = Category.objects.create(name='Applied')
        self.status_interview = Category.objects.create(name='Interview')

    def test_status_changed_at_set_on_status_change(self):
        job = JobApplication.objects.create(
            title='Developer', company='Acme',
            owner=self.user, status=self.status_applied,
        )
        self.assertIsNone(job.status_changed_at)

        job.status = self.status_interview
        job.save()
        job.refresh_from_db()

        self.assertIsNotNone(job.status_changed_at)

    def test_status_changed_at_not_set_when_status_unchanged(self):
        job = JobApplication.objects.create(
            title='Developer', company='Acme',
            owner=self.user, status=self.status_applied,
        )
        job.title = 'Senior Developer'
        job.save()
        job.refresh_from_db()

        self.assertIsNone(job.status_changed_at)

    def test_str(self):
        job = JobApplication.objects.create(
            title='Developer', company='Acme',
            owner=self.user, status=self.status_applied,
        )
        self.assertEqual(str(job), 'Developer у Acme')


class DashboardViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.status = Category.objects.create(name='Applied')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/', response['Location'])

    def test_dashboard_loads_for_logged_in_user(self):
        self.client.login(username='testuser', password='pass1234')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/dashboard.html')

    def test_dashboard_shows_only_own_jobs(self):
        other = User.objects.create_user(username='other', password='pass1234')
        JobApplication.objects.create(title='Mine', company='A', owner=self.user, status=self.status)
        JobApplication.objects.create(title='Theirs', company='B', owner=other, status=self.status)

        self.client.login(username='testuser', password='pass1234')
        response = self.client.get(reverse('dashboard'))
        jobs = list(response.context['page_obj'])

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].title, 'Mine')


class JobCRUDViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.status = Category.objects.create(name='Applied')
        self.client.login(username='testuser', password='pass1234')

    def test_create_job(self):
        response = self.client.post(reverse('job_create'), {
            'title': 'Developer',
            'company': 'Acme',
            'status': self.status.pk,
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(JobApplication.objects.count(), 1)

    def test_cannot_view_other_users_job(self):
        other = User.objects.create_user(username='other', password='pass1234')
        job = JobApplication.objects.create(
            title='Secret', company='X', owner=other, status=self.status
        )
        response = self.client.get(reverse('job_detail', args=[job.pk]))
        self.assertEqual(response.status_code, 404)

    def test_delete_job(self):
        job = JobApplication.objects.create(
            title='Dev', company='A', owner=self.user, status=self.status
        )
        response = self.client.post(reverse('job_delete', args=[job.pk]))
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(JobApplication.objects.count(), 0)


class EventModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.status = Category.objects.create(name='Applied')
        self.job = JobApplication.objects.create(
            title='Dev', company='Acme', owner=self.user, status=self.status
        )

    def test_event_str(self):
        event = Event.objects.create(
            job=self.job,
            title='Перша співбесіда',
            date=timezone.now(),
            event_type='interview',
        )
        self.assertIn('Перша співбесіда', str(event))
