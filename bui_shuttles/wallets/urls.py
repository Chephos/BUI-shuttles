from django.urls import path
from rest_framework import routers

from bui_shuttles.wallets import views

app_name = "wallets"

router = routers.DefaultRouter()
router.register("transactions", views.Transaction, basename="transaction")
urlpatterns = [
    path("banks/", views.BanksList.as_view(), name="banks"),
    path(
        "bank_account_name/", views.BankAccountName.as_view(), name="bank_account_name"
    ),
    path("webhook/", views.PaystackWebhooks.as_view(), name="paystack_webhook"),
]
urlpatterns += router.urls
