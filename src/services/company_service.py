from flask import g

from src.payloads.dtos.company_dto import CompanyDto
from src.repositories.company_repository import get_company_by_company_id


def get_company_profile():
    company_id = g.company_id

    company = get_company_by_company_id(company_id)

    return CompanyDto(company)