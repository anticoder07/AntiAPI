from datetime import datetime

from src.commons.database.mySql.config_connect_my_sql import db
from src.models.project import Project


def save_project(project_name, company_id, password):
    new_project = Project(
        company_id=company_id,
        project_name=project_name,
        password=password,
        updated_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )

    db.session.add(new_project)
    db.session.commit()
    return new_project

def get_projects_by_company_id(company_id):
    return Project.query.filter_by(company_id=company_id)

def get_project_by_project_id(project_id):
    return Project.query.filter_by(project_id=project_id).first()

def delete_project_by_project_id(project_id):
    return Project.query.filter_by(project_id=project_id).delete()
