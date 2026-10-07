from django.contrib import admin
from .models import InterviewSession, Question, UserProfile


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ('order', 'text', 'user_answer', 'score', 'feedback')
    readonly_fields = ('feedback', 'score')


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'difficulty', 'completed', 'score', 'created_at')
    list_filter = ('role', 'difficulty', 'completed')
    search_fields = ('user__username',)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('session', 'order', 'text', 'score')
    list_filter = ('session__role',)
    search_fields = ('text',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_role', 'total_sessions', 'average_score')
