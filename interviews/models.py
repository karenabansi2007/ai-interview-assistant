from django.db import models
from django.contrib.auth.models import User


class InterviewSession(models.Model):
    ROLE_CHOICES = [
        ('software_engineer', 'Software Engineer'),
        ('data_scientist', 'Data Scientist'),
        ('product_manager', 'Product Manager'),
        ('devops_engineer', 'DevOps Engineer'),
        ('frontend_developer', 'Frontend Developer'),
        ('backend_developer', 'Backend Developer'),
        ('fullstack_developer', 'Full-Stack Developer'),
        ('ml_engineer', 'ML Engineer'),
        ('other', 'Other'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} – {self.get_role_display()} ({self.created_at:%Y-%m-%d})"

    def question_count(self):
        return self.questions.count()

    def answered_count(self):
        return self.questions.filter(user_answer__isnull=False).exclude(user_answer='').count()


class Question(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    ai_answer = models.TextField(blank=True, help_text='Model answer / guidance provided by AI')
    user_answer = models.TextField(blank=True)
    feedback = models.TextField(blank=True, help_text='AI feedback on the user answer')
    score = models.FloatField(null=True, blank=True, help_text='Score 0–10 for this answer')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Q{self.order}: {self.text[:60]}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    target_role = models.CharField(max_length=100, blank=True)
    total_sessions = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"
