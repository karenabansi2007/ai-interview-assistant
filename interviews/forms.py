from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import InterviewSession, Question, UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class StartSessionForm(forms.ModelForm):
    class Meta:
        model = InterviewSession
        fields = ('role', 'difficulty')
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('user_answer',)
        widgets = {
            'user_answer': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Type your answer here…',
            }),
        }
        labels = {'user_answer': 'Your Answer'}


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'target_role')
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'target_role': forms.TextInput(attrs={'class': 'form-control'}),
        }
