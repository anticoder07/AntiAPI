import re
from datetime import timedelta, datetime
from http import HTTPStatus

from flask_jwt_extended import create_access_token

from src.commons.exception.custom_exception.custom_exception import CustomException
from src.models.e_company_status import ECompanyStatus
from src.models.e_customer_type import ECustomerType
from src.payloads.dtos.company_dto import CompanyDto
from src.payloads.responses.authentication_response import AuthenticationResponse
from src.repositories.company_repository import get_company_by_username, save_company, exist_company_by_user_name
from src.repositories.token_repository import save_token
from src.services.auth.password_service import hash_password, verify_password


def create_account(data):
    validate_user_data_sign_up(data)

    if exist_company_by_user_name(data.get('user_name')) is True:
        raise CustomException('Account already exists', HTTPStatus.CONFLICT)

    hashed_password = hash_password(data['password'])

    save_company(
        company_name=data.get('company_name'),
        user_name=data.get('user_name'),
        password=hashed_password,
        status=ECompanyStatus.ACTIVE.value
    )

    return "Create account successfully"


def login_company(data):
    if not data.get('user_name'):
        raise CustomException("User name cannot be null or empty", HTTPStatus.BAD_REQUEST)
    if not data.get('password'):
        raise CustomException("Password cannot be null or empty", HTTPStatus.BAD_REQUEST)

    company = get_company_by_username(data['user_name'])
    if company is None:
        raise CustomException('Company not found', HTTPStatus.NOT_FOUND)

    if not verify_password(data['password'], company.password):
        raise CustomException('Invalid password', HTTPStatus.BAD_REQUEST)

    access_token = create_access_token(
        identity=str(company.company_id),
        expires_delta=timedelta(hours=1)
    )

    expires_at = datetime.utcnow() + timedelta(hours=1)

    save_token(
        company.company_id,
        ECustomerType.COMPANY.value,
        access_token,
        expires_at
    )

    auth_res = AuthenticationResponse(
        CompanyDto(company),
        access_token
    )

    return auth_res


def validate_user_data_sign_up(data):
    required_fields = ['company_name', 'user_name', 'password', 'password_confirmation']
    for field in required_fields:
        if not data.get(field):
            raise CustomException(f"{field.replace('_', ' ').capitalize()} cannot be null or empty",
                                  HTTPStatus.BAD_REQUEST)

    if data['password'] != data['password_confirmation']:
        raise CustomException("Passwords do not match", HTTPStatus.BAD_REQUEST)

    password = data['password']
    if len(password) < 8:
        raise CustomException("Password must be at least 8 characters long", HTTPStatus.BAD_REQUEST)

    if not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+={}[\]|\\:;"<>,.?/~`]).+$', password):
        raise CustomException(
            "Password must contain at least one uppercase letter, one number, and one special character",
            HTTPStatus.BAD_REQUEST)

    email = data['user_name']
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        raise CustomException("Invalid email format", HTTPStatus.BAD_REQUEST)

    if not data['company_name'].strip():
        raise CustomException("Company name cannot be empty or just spaces", HTTPStatus.BAD_REQUEST)

    return True
