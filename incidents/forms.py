from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Incident, AnonymousReport

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['title', 'description', 'category', 'latitude', 'longitude', 'date_occurred', 'place']
        widgets = {
            'date_occurred': forms.DateInput(attrs={'type': 'date'}),
            'latitude': forms.NumberInput(attrs={'step': 'any', 'readonly': 'readonly'}),
            'longitude': forms.NumberInput(attrs={'step': 'any', 'readonly': 'readonly'}),
        }
        labels = {
            'title': 'Заголовок',
            'description': 'Описание',
            'category': 'Категория',
            'latitude': 'Широта',
            'longitude': 'Долгота',
            'date_occurred': 'Дата происшествия',
            'place': 'Адрес места',
        }

    class Meta:
        model = Incident
        fields = ['title', 'description', 'category', 'latitude', 'longitude', 'date_occurred', 'place']
        widgets = {
            'date_occurred': forms.DateInput(attrs={'type': 'date'}),
            'latitude': forms.NumberInput(attrs={'step': 'any', 'readonly': 'readonly'}),
            'longitude': forms.NumberInput(attrs={'step': 'any', 'readonly': 'readonly'}),
        }

class AnonymousReportForm(forms.ModelForm):
    class Meta:
        model = AnonymousReport
        fields = ['subject', 'message', 'location']
