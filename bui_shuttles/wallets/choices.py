from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

class TransactionStatus(TextChoices):
    pending = "pending", _("Pending")
    successful = "successful", _("Successful")
    failed = "failed", _("Failed")

class TransactionType(TextChoices):
    credit = "credit", _("Credit")
    debit = "debit", _("Debit")
