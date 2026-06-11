# accounts/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('profile/', views.ProfileView.as_view()),
    path('referrals/', views.ReferralHistoryView.as_view()),
    path('myreferrals/', views.MyReferralsView.as_view()),
]