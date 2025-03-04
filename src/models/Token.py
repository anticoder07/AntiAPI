from src.models.ECustomerType import ECustomerType


class Token:
    def __init__(self, token_id, customer_id, customer_type: ECustomerType, token, expires_at):
        self.token_id = token_id
        self.customer_id = customer_id
        self.customer_type = customer_type
        self.token = token
        self.expires_at = expires_at
