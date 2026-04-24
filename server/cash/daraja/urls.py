# mpesa/urls.py

from django.urls import path
from .views import STKPushView, MpesaCallbackView

urlpatterns = [
    path("stk-push/", STKPushView.as_view(), name="stk_push"),
    path("callback/", MpesaCallbackView.as_view(), name="mpesa_callback"),
]