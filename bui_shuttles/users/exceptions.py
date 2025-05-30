from rest_framework.exceptions import APIException

class OTPVerificationFailed(APIException):
    status_code = 403
    default_detail = "OTP verification failed or expired for phone number"
    default_code = "otp_verification_failed_or_expired"

class UserAlreadyExists(APIException):
    status_code = 400
    default_detail = "User with this email already exists"
    default_code = "user_already_exists"

class InvalidOTP(APIException):
    status_code = 400
    default_detail = "Invalid OTP"
    default_code = "invalid_otp"

class BankVerificationFailed(APIException):
    status_code = 403
    default_detail = "Bank details verification failed"
    default_code = "bank_verification_failed"