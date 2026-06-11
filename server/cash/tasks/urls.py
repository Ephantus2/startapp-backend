from django.urls import path
from .views import (
    TaskListView,
    CompleteTaskView
)

urlpatterns = [
    path('', TaskListView.as_view()),
    path('complete/', CompleteTaskView.as_view()),
]