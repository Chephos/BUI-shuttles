import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError

from bui_shuttles.utils import types
from bui_shuttles.services.base import BaseService


class PaystackService(BaseService):
    def __init__(self):
        self.base_url = "https://api.paystack.co"
        self.headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

    def _response_validator(self, response: dict) -> bool:
        if response["status"] is False:
            raise ValidationError(response["message"])
        return True


    def get_account_name(self, account_number: str, bank_code: str) -> str:
        """
        Get account name from account number and bank code
        :param account_number: account number
        :param bank_code: bank code
        :return: account name
        """
        endpoint = f"/bank/resolve?account_number={account_number}&bank_code={bank_code}"
        response = self._call(requests.get, endpoint)
        return response["data"]["account_name"]

    def get_banks(self) -> list:
        """
        Get a list of all banks in nigeria supported by paystack
        :return: list of bank dicts. E.g [{"name": "Access Bank", "code": "044", "slug": "access-bank"}]
        """
        endpoint = "/bank?country=nigeria"
        response = self._call(requests.get, endpoint)
        return response["data"]

    
    
    def initialize_transaction(
        self,
        amount: int,
        customer_email: str,
        transaction_reference: str,
        callback_url: str = None,
        metadata: dict | None = None,
    ) -> types.PaystackTransaction:
        endpoint = "/transaction/initialize"
        amount_kobo = int(amount * 100)
        payload = {
            "amount": amount_kobo,
            "email": customer_email,
            "reference": transaction_reference,
            "callback_url": callback_url,
            "metadata": metadata,
        }
        response = self._call(requests.post, endpoint, payload)
        return types.PaystackTransaction(**response["data"])
