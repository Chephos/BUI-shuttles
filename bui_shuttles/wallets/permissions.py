import hmac

from rest_framework.permissions import AllowAny

from bui_shuttles.wallets import workers


class PaystackPermission(AllowAny):
    def has_permission(self, request, view):
        paystack_signature = request.headers.get("x-paystack-signature")
        generated_signature = workers.Paystack.generate_signature(request.body)
        if paystack_signature is None:
            return False
        return hmac.compare_digest(paystack_signature, generated_signature)
