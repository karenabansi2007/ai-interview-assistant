from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('sessions/', views.session_list, name='session_list'),
    path('sessions/start/', views.start_session, name='start_session'),
    path('sessions/<int:pk>/', views.session_detail, name='session_detail'),
    path('sessions/<int:pk>/results/', views.session_results, name='session_results'),
    path('sessions/<int:session_pk>/answer/<int:question_pk>/', views.answer_question, name='answer_question'),
    path('profile/', views.profile_view, name='profile'),
]
