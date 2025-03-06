from src.payloads.dtos.company_dto import CompanyDto


class AuthenticationResponse:
    def __init__(self, company: CompanyDto, token):
        self.company = company
        self.token = token

    def to_dict(self):
        return {
            'company': self.company.to_dict(),
            'token': self.token,
        }