from abc import ABCMeta, abstractmethod
from collections.abc import Callable

from rest_framework.exceptions import ValidationError


class BaseService(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        self.headers = {}
        self.base_url = ""

    def _response_validator(self, response: dict) -> bool:
        """
        Validate response from third party api
        :param response: response from third party api
        :return: bool
        """
        return True

    def _call(
        self,
        method: Callable,
        endpoint: str,
        data: dict | None = None,
        status_code: int | None = 200,
    ) -> dict:
        """
        Send request to Third party API service and handle errors
        :param method: requests package method
        :param endpoint: endpoint to send request to
        :param data: request body
        :return: dict response from api
        """
        response = method(self.base_url + endpoint, json=data, headers=self.headers)
        data = response.json()
        if response.status_code != status_code:
            raise ValidationError(data["message"])

        if self._response_validator(data):
            return data
        raise ValidationError(data["message"])
