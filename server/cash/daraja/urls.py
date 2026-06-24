# mpesa/urls.py

from django.urls import path
from .views import STKPushView, MpesaCallbackView

from django.urls import path

from .views import (
    WithdrawView,
    B2CCallbackView,
    B2CTimeoutView
)



urlpatterns = [
    path("stk-push/", STKPushView.as_view(), name="stk_push"),
    path("callback/", MpesaCallbackView.as_view(), name="mpesa_callback"),
     path(
        'withdraw/',
        WithdrawView.as_view()
    ),

    path(
        'b2c-callback/',
        B2CCallbackView.as_view()
    ),
    path(
        "b2c-timeout/",
        B2CTimeoutView.as_view()
    ),
]