from datetime import datetime

from src.commons.database.mySql.config_connect_my_sql import db
from src.models.project import Project


def save_project(project_name, company_id):
    new_project = Project(
        company_id=company_id,
        project_name=project_name,
        updated_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )

    db.session.add(new_project)
    db.session.commit()
    return new_project


def get_projects_by_company_id(company_id):
    return Project.query.filter_by(company_id=company_id).all()


def get_project_by_project_id(project_id):
    return Project.query.filter_by(project_id=project_id).first()


def update_project_name(project_id, project_name):
    project = get_project_by_project_id(project_id)
    if project:
        project.project_name = project_name
        project.updated_at = datetime.utcnow()
        db.session.commit()
    return project


def delete_project_by_project_id(project_id):
    project = get_project_by_project_id(project_id)
    if project:
        db.session.delete(project)
        db.session.commit()
        return True
    return False
