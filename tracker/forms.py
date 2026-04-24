from django import forms
from .models import JobApplication, Event

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['title', 'company', 'url', 'description', 'status']


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'date', 'event_type']
        widgets = {
            'date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Щоб форма коректно рендерила початкове значення
        self.fields['date'].input_formats = ['%Y-%m-%dT%H:%M']