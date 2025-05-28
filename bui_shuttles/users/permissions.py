from rest_framework import permissions

from bui_shuttles.users import choices

class IsStudent(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return request.user.account_type == choices.AccountType.student.value

class IsDriver(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return request.user.account_type == choices.AccountType.driver.value
        
class HasBankDetails(IsDriver):
    
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return (
                request.user.driver.bank_account_number is not None
                and request.user.driver.bank_account_name is not None
                and request.user.driver.bank_code is not None
            )