from flask import Blueprint, render_template, url_for, request

base_web_url = Blueprint('base_web_url', __name__)


@base_web_url.route('/page', methods=['GET'])
def page():
    return render_template(
        'base/layout.html',
        api_type='HELLO',
        api_endpoint='Welcome to ANTIAPI',
        content_template='pages/project-page.html',
        sidebar_template='',
        title_hide='NO',
    )

@base_web_url.route('/page/project', methods=['GET'])
def page_render_project():
    api_endpoint = request.args.get('id')
    return render_template(
        'base/layout.html',
        sidebar_template='components/sidebar.html',
        content_template='',
        api_type='',
        api_endpoint=''
    )

@base_web_url.route('/page/scan', methods=['GET'])
def page_render_scan():
    api_endpoint = request.args.get('pid')
    return render_template(
        'base/layout.html',
        api_type='SCAN',
        api_endpoint='ANTIAPI',
        content_template='pages/analist-page.html',
        sidebar_template='',
        title_hide='NO',
    )


@base_web_url.route('/page/<api_type>', methods=['GET'])
def page_render(api_type):
    api_endpoint = request.args.get('ae', '/scan/v1/resource')
    return render_template(
        'base/layout.html',
        api_type=api_type,
        api_endpoint=api_endpoint
    )


@base_web_url.route('/sign-up', methods=['GET'])
def page_sign_up():
    return render_template(
        'base/layout-auth.html',
        title='Welcome to AntiAPI',
        introduce='Access our powerful tools and services to enhance your business workflow',
        form_template='components/sign-up-section.html',
        redirect_login=url_for('base_web_url.page_login')
    )


@base_web_url.route('/login', methods=['GET'])
def page_login():
    return render_template(
        'base/layout-auth.html',
        title='Login to AntiAPI',
        introduce='Securely access your account',
        form_template='components/login-section.html',
        redirect_forgot_pwd=url_for('base_web_url.page_forgot_pwd'),
        redirect_sign_up=url_for('base_web_url.page_sign_up')
    )


@base_web_url.route('/forgot/password', methods=['GET'])
def page_forgot_pwd():
    return render_template(
        'base/layout-auth.html',
        title='Supported by AntiAPI',
        introduce="We'll help you reset your password and get back to your account",
        form_template='components/forgot-password-section.html',
        redirect_login=url_for('base_web_url.page_login')
    )


@base_web_url.route('/forgot/password/change', methods=['GET'])
def page_change_pwd():
    return render_template(
        'base/layout-auth.html',
        title='Supported by AntiAPI',
        introduce='Secure your account by updating your password',
        form_template='components/change-password-section.html',
        redirect_login=url_for('base_web_url.page_login')
    )


@base_web_url.route('/forgot/password/otp', methods=['GET'])
def page_check_otp_pwd():
    return render_template(
        'base/layout-auth.html',
        title='Supported by AntiAPI',
        introduce='Almost there, keep it up!',
        form_template='components/otp-password-section.html',
        redirect_login=url_for('base_web_url.page_login')
    )
