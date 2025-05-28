from django.shortcuts import render

from rest_framework import views, response, status

from bui_shuttles.wallets import workers, permissions, serializers

class BanksList(views.APIView):
    def get(self, request, *args, **kwargs):
        banks = workers.Paystack.get_banks()
        return response.Response(data=banks, status=status.HTTP_200_OK)


class BankAccountName(views.APIView):
    def get(self, request, *args, **kwargs):
        account_name = workers.Paystack.get_account_name(
            account_number=request.query_params.get("account_number"), bank_code=request.query_params.get("bank_code")
        )
        return response.Response(data={"account_name": account_name}, status=status.HTTP_200_OK)

class PaystackWebhooks(views.APIView):
    permission_classes = [permissions.PaystackPermission]
    serializers_class = serializers.Paystack

    def post(self, request, *args, **kwargs):
        serializer = self.serializers_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        event = data["event"].split(".")[0]
        event_helper_map = {
            "charge": workers.Paystack.process_charge_event,
        }
        helper_function = event_helper_map.get(event)
        if helper_function:
            helper_function(data["event"], data["data"])
        else:
            return response.Response(status=status.HTTP_404_NOT_FOUND, data={})
        return response.Response(status=status.HTTP_200_OK, data={})
