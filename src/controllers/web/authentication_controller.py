from flask import Blueprint, render_template
from src.models import Company

base_web_url = Blueprint('base_web_url', __name__)

@base_web_url.route('/page', methods=['GET'])
def page():
    return render_template(
        'base/layout.html',
        api_type='GET',
        api_endpoint='/api/v1/resource'
    )
