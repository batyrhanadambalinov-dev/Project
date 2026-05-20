from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Task

class UserRegisterForm(UserCreationForm):
    pass

class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'subject', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }