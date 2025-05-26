import dataclasses

@dataclasses.dataclass
class PaystackTransaction:
    authorization_url: str
    access_code: str
    reference: str