import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Avg

from .models import InterviewSession, Question, UserProfile
from .forms import RegisterForm, StartSessionForm, AnswerForm, UserProfileForm


# ---------------------------------------------------------------------------
# Sample question bank (in production replace with AI API call)
# ---------------------------------------------------------------------------
QUESTION_BANK = {
    'software_engineer': [
        "Explain the difference between a stack and a queue.",
        "What is Big-O notation? Give an example.",
        "Describe the SOLID principles.",
        "How does garbage collection work in Python?",
        "What is the difference between concurrency and parallelism?",
        "Explain what a RESTful API is.",
        "What are design patterns? Name three common ones.",
        "How would you optimise a slow database query?",
    ],
    'data_scientist': [
        "What is the bias-variance tradeoff?",
        "Explain overfitting and how to prevent it.",
        "What is cross-validation and why is it used?",
        "Describe the steps in a typical machine learning pipeline.",
        "What is the difference between supervised and unsupervised learning?",
        "How do you handle missing data?",
        "What is regularisation?",
        "Explain precision vs recall.",
    ],
    'product_manager': [
        "How do you prioritise a product backlog?",
        "Describe a time you used data to make a product decision.",
        "What is a product roadmap and how do you build one?",
        "How do you handle conflicting stakeholder priorities?",
        "What metrics would you track for a new feature launch?",
        "Explain the concept of MVP.",
        "How do you gather user feedback?",
        "Describe your process for writing a PRD.",
    ],
    'devops_engineer': [
        "What is CI/CD and why is it important?",
        "Explain infrastructure as code.",
        "What is a container and how does Docker work?",
        "Describe the blue-green deployment strategy.",
        "What is Kubernetes and what problems does it solve?",
        "How do you monitor a production system?",
        "What is the difference between horizontal and vertical scaling?",
        "Explain the concept of immutable infrastructure.",
    ],
    'frontend_developer': [
        "What is the virtual DOM?",
        "Explain the CSS box model.",
        "What is the difference between `==` and `===` in JavaScript?",
        "What are closures in JavaScript?",
        "Explain responsive design.",
        "What is CORS and how does it work?",
        "Describe the event loop in JavaScript.",
        "What is accessibility (a11y) and why does it matter?",
    ],
    'backend_developer': [
        "What is an ORM and what are its pros/cons?",
        "Explain database indexing.",
        "What is the difference between SQL and NoSQL?",
        "How do sessions and cookies work?",
        "What is caching and when would you use it?",
        "Describe how a web server handles an HTTP request.",
        "What are database transactions and ACID properties?",
        "How do you secure a REST API?",
    ],
    'fullstack_developer': [
        "What is the difference between server-side and client-side rendering?",
        "How do you manage state in a modern web application?",
        "Explain JWT-based authentication.",
        "What is a microservices architecture?",
        "How would you design a URL shortener?",
        "What is WebSocket and when would you use it?",
        "Describe your approach to debugging a production issue.",
        "What are environment variables and why are they important?",
    ],
    'ml_engineer': [
        "What is model drift and how do you detect it?",
        "Explain the difference between a batch and online learning system.",
        "How do you deploy a machine learning model to production?",
        "What is feature engineering?",
        "Explain gradient descent.",
        "What is a confusion matrix?",
        "How do you version control ML experiments?",
        "What is transfer learning?",
    ],
    'other': [
        "Tell me about yourself.",
        "Describe a challenging project you worked on.",
        "How do you prioritise your tasks?",
        "What is your greatest technical strength?",
        "Where do you see yourself in 5 years?",
        "Describe a time you had to learn something quickly.",
        "How do you handle constructive criticism?",
        "What does success look like to you?",
    ],
}

NUM_QUESTIONS = 5


def _get_questions(role):
    pool = QUESTION_BANK.get(role, QUESTION_BANK['other'])
    return random.sample(pool, min(NUM_QUESTIONS, len(pool)))


def _get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


# ---------------------------------------------------------------------------
# Auth views
# ---------------------------------------------------------------------------

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        _get_or_create_profile(user)
        login(request, user)
        messages.success(request, f"Welcome, {user.username}! Your account has been created.")
        return redirect('dashboard')
    return render(request, 'interviews/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f"Welcome back, {user.username}!")
        return redirect('dashboard')
    return render(request, 'interviews/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ---------------------------------------------------------------------------
# Core views
# ---------------------------------------------------------------------------

@login_required
def dashboard(request):
    sessions = InterviewSession.objects.filter(user=request.user)
    profile = _get_or_create_profile(request.user)
    stats = {
        'total': sessions.count(),
        'completed': sessions.filter(completed=True).count(),
        'avg_score': sessions.filter(score__isnull=False).aggregate(a=Avg('score'))['a'],
    }
    recent = sessions[:5]
    return render(request, 'interviews/dashboard.html', {
        'profile': profile,
        'stats': stats,
        'recent': recent,
    })


@login_required
def start_session(request):
    form = StartSessionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        session = form.save(commit=False)
        session.user = request.user
        session.save()
        questions = _get_questions(session.role)
        for i, text in enumerate(questions, start=1):
            Question.objects.create(session=session, text=text, order=i)
        return redirect('session_detail', pk=session.pk)
    return render(request, 'interviews/start_session.html', {'form': form})


@login_required
def session_detail(request, pk):
    session = get_object_or_404(InterviewSession, pk=pk, user=request.user)
    questions = session.questions.all()
    return render(request, 'interviews/session_detail.html', {
        'session': session,
        'questions': questions,
    })


@login_required
def answer_question(request, session_pk, question_pk):
    session = get_object_or_404(InterviewSession, pk=session_pk, user=request.user)
    question = get_object_or_404(Question, pk=question_pk, session=session)

    if session.completed:
        return redirect('session_detail', pk=session.pk)

    form = AnswerForm(request.POST or None, instance=question)
    if request.method == 'POST' and form.is_valid():
        q = form.save(commit=False)
        # Simulated AI feedback (replace with real LLM call)
        q.feedback = _generate_feedback(q.user_answer, q.text)
        q.score = _score_answer(q.user_answer)
        q.ai_answer = _model_answer(q.text, session.role)
        q.save()

        # Check if all questions answered
        all_done = not session.questions.filter(user_answer='').exists()
        if all_done:
            avg = session.questions.aggregate(a=Avg('score'))['a'] or 0
            session.score = round(avg, 1)
            session.completed = True
            session.save()
            _update_profile_stats(request.user)
            messages.success(request, "Interview complete! Here are your results.")
            return redirect('session_results', pk=session.pk)

        next_q = session.questions.filter(user_answer='').first()
        return redirect('answer_question', session_pk=session.pk, question_pk=next_q.pk)

    return render(request, 'interviews/answer_question.html', {
        'session': session,
        'question': question,
        'form': form,
        'progress': _progress(session),
    })


@login_required
def session_results(request, pk):
    session = get_object_or_404(InterviewSession, pk=pk, user=request.user)
    questions = session.questions.all()
    return render(request, 'interviews/session_results.html', {
        'session': session,
        'questions': questions,
    })


@login_required
def session_list(request):
    sessions = InterviewSession.objects.filter(user=request.user)
    return render(request, 'interviews/session_list.html', {'sessions': sessions})


@login_required
def profile_view(request):
    profile = _get_or_create_profile(request.user)
    form = UserProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect('profile')
    return render(request, 'interviews/profile.html', {'form': form, 'profile': profile})


# ---------------------------------------------------------------------------
# Helpers (stub AI functions — swap with real LLM calls)
# ---------------------------------------------------------------------------

def _generate_feedback(answer, question):
    if not answer.strip():
        return "No answer provided."
    length = len(answer.split())
    if length < 10:
        return "Your answer is very brief. Consider elaborating with examples or details."
    if length < 30:
        return "Good start! Adding concrete examples would strengthen your answer."
    return "Well-structured answer. Review the model answer below to see if there are points you may have missed."


def _score_answer(answer):
    words = len(answer.split())
    if words == 0:
        return 0.0
    if words < 10:
        return round(min(3.0, words * 0.3), 1)
    if words < 50:
        return round(min(7.0, 3.0 + (words - 10) * 0.1), 1)
    return round(min(10.0, 7.0 + (words - 50) * 0.02), 1)


def _model_answer(question_text, role):
    return (
        f'A strong answer to "{question_text}" would cover the core concept clearly, '
        f"provide a concrete example relevant to a {role.replace('_', ' ')} role, "
        "and conclude with real-world implications or trade-offs."
    )


def _progress(session):
    total = session.questions.count()
    answered = session.questions.exclude(user_answer='').count()
    pct = int((answered / total) * 100) if total else 0
    return {'answered': answered, 'total': total, 'pct': pct}


def _update_profile_stats(user):
    profile = _get_or_create_profile(user)
    sessions = InterviewSession.objects.filter(user=user, completed=True)
    profile.total_sessions = sessions.count()
    avg = sessions.aggregate(a=Avg('score'))['a']
    profile.average_score = round(avg, 1) if avg else None
    profile.save()
