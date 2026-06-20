from django.urls import path
from .views import (
    TaskListView,
    CompleteTaskView,
    TransactionsView
)

urlpatterns = [
    path('', TaskListView.as_view()),
    path('complete/', CompleteTaskView.as_view()),
    path('transactions/', TransactionsView.as_view())
]