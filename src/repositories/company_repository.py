from datetime import datetime
from http import HTTPStatus

from src.commons.database.mySql.config_connect_my_sql import db
from src.commons.exception.custom_exception.custom_exception import CustomException
from src.models.company import Company


def save_company(company_name, user_name, password, status):
    try:
        new_company = Company(
            company_name=company_name,
            user_name=user_name,
            password=password,
            status=status,
            created_at=datetime.utcnow()
        )

        db.session.add(new_company)
        db.session.commit()
        return new_company
    except Exception as e:
        db.session.rollback()
        print(f"Error creating company: {e}")
        raise CustomException('Error creating company', HTTPStatus.INTERNAL_SERVER_ERROR)


def get_company_by_company_id(company_id):
    company = Company.query.get(company_id)
    return company

def get_company_by_username(user_name):
    return Company.query.filter_by(user_name=user_name).first()

def exist_company_by_user_name(user_name):
    return Company.query.filter(Company.user_name == user_name).first() is not None
