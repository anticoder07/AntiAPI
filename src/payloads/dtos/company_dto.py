class CompanyDto:
    def __init__(self, data):
        self.id = getattr(data, 'company_id', None)
        self.company_name = getattr(data, 'company_name', None)
        self.user_name = getattr(data, 'user_name', None)
        self.status = getattr(data, 'status', None)
        self.created_at = getattr(data, 'created_at', None)

    def to_dict(self):
        return {
            'company_id': self.id,
            'company_name': self.company_name,
            'user_name': self.user_name,
            'status': self.status,
            'created_at': self.created_at,
        }
