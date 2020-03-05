from flask import render_template, redirect, request, Blueprint, current_app
from ulapd_ui.utils.session import dps_session
from ulapd_ui.dependencies.ulapd_api import UlapdAPI
from ulapd_ui.utils.registration_data import collect_personal_info, collect_organisation_info, \
     collect_organisation_type, collect_charity_details, collect_company_details
from ulapd_ui.utils.registration_utilities import in_session, add_personal_info_validators, \
     add_org_info_validators, populate_session, fetch_registration, add_charity_details_validators, \
     add_company_details_validators
from ulapd_ui.utils.validation import FormValidator, org_type_validator

registration_uk_organisation = Blueprint('registration_uk_organisation', __name__, url_prefix="/registration")


@registration_uk_organisation.route('/about-you-uk-organisation', methods=['GET'])
def get_personal_info_page():
    if _session_invalid('user_type'):
        return redirect('/registration')

    return render_template('app/registration/personal_information.html', route='about-you-uk-organisation')


@registration_uk_organisation.route('/about-you-uk-organisation', methods=['POST'])
def submit_personal_info():
    if _session_invalid('user_type'):
        return redirect('/registration')

    personal_info = collect_personal_info(request.form, 'org')

    form = add_personal_info_validators(personal_info, 'org')

    if form.is_valid():
        session = populate_session(personal_info)
        dps_session.commit()
        if 'changing_answers' in session['registration']:
            return redirect('/registration/check-your-answers-uk-organisation')
        return redirect('/registration/organisation-type')
    else:
        return render_template('app/registration/personal_information.html',
                               error_title="There are errors on this page",
                               route='about-you-uk-organisation',
                               fields=form.validate())


@registration_uk_organisation.route('/organisation-type', methods=['GET'])
def get_org_type_page():
    if _session_invalid(['title']):
        return redirect('/registration/about-you-uk-organisation')

    return render_template('app/registration/org_uk_type.html')


@registration_uk_organisation.route('/organisation-type', methods=['POST'])
def submit_org_type():
    if _session_invalid(['title']):
        return redirect('/registration/about-you-uk-organisation')

    org_type = collect_organisation_type(request.form)
    form = _add_org_type_validators(org_type)

    if form.is_valid():
        populate_session(org_type, prefix='uk_org_')
        dps_session.commit()

        if org_type.type == 'Company':
            return redirect('/registration/company-details')
        elif org_type.type == 'Charity':
            return redirect('/registration/charity-details')
        else:
            return redirect('/registration/about-your-organisation-uk')

    else:
        return render_template('app/registration/org_uk_type.html',
                               error_title="There are errors on this page",
                               fields=form.validate())


@registration_uk_organisation.route('/company-details', methods=['GET'])
def get_org_details_page():
    if _session_invalid(['uk_org_type']):
        return redirect('/registration/company-details')

    return render_template('app/registration/company_details.html')


@registration_uk_organisation.route('/company-details', methods=['POST'])
def submit_org_details():
    if _session_invalid(['uk_org_type']):
        return redirect('/registration/about-you-uk-organisation')

    company_details = collect_company_details(request.form)
    form = add_company_details_validators(company_details)

    if form.is_valid():
        session = populate_session(company_details, prefix='uk_org_')
        dps_session.commit()

        if 'changing_answers' in session['registration']:
            return redirect('/registration/check-your-answers-uk-organisation')

        return redirect('/registration/about-your-organisation-uk')

    else:
        return render_template('app/registration/company_details.html',
                               error_title="There are errors on this page",
                               fields=form.validate())


@registration_uk_organisation.route('/charity-details', methods=['GET'])
def get_charity_details_page():
    if _session_invalid(['uk_org_type']):
        return redirect('/registration/charity-details')

    return render_template('app/registration/charity_details.html')


@registration_uk_organisation.route('/charity-details', methods=['POST'])
def submit_charity_details():
    if _session_invalid(['uk_org_type']):
        return redirect('/registration/about-you-uk-organisation')

    charity_details = collect_charity_details(request.form)
    form = add_charity_details_validators(charity_details)

    if form.is_valid():
        session = populate_session(charity_details, prefix='uk_org_')
        dps_session.commit()

        if 'changing_answers' in session['registration']:
            return redirect('/registration/check-your-answers-uk-organisation')

        return redirect('/registration/about-your-organisation-uk')

    else:
        return render_template('app/registration/charity_details.html',
                               error_title="There are errors on this page",
                               fields=form.validate())


@registration_uk_organisation.route('/about-your-organisation-uk', methods=['GET'])
def get_org_info_page():
    if _session_invalid(['uk_org_type']):
        return redirect('/registration/about-you-uk-organisation')

    return render_template('app/registration/org_information_uk.html')


@registration_uk_organisation.route('/about-your-organisation-uk', methods=['POST'])
def submit_org_info():
    if _session_invalid(['uk_org_type']):
        return redirect('/registration/about-you-uk-organisation')

    org_info = collect_organisation_info(request.form)
    bypass = False
    if org_info.type == 'Charity' or org_info.type == 'Company':
        bypass = True
    form = add_org_info_validators(org_info, bypass)

    if form.is_valid():
        session = populate_session(org_info, prefix='uk_org_')
        dps_session.commit()

        if 'changing_answers' in session['registration']:
            return redirect('/registration/check-your-answers-uk-organisation')
        return redirect('/registration/research')
    else:
        return render_template('app/registration/org_information_uk.html',
                               error_title="There are errors on this page",
                               fields=form.validate())


@registration_uk_organisation.route('/check-your-answers-uk-organisation', methods=['GET'])
def get_check_your_answers_page():
    if _session_invalid(['uk_org_type', 'changing_answers']):
        return redirect('/registration/about-your-organisation-uk')
    return render_template('app/registration/check-your-answers-uk-org.html')


@registration_uk_organisation.route('/check-your-answers-uk-organisation', methods=['POST'])
def submit_answers():
    if _session_invalid(['uk_org_type', 'changing_answers']):
        return redirect('/registration/about-your-organisation-uk')

    if 'terms' not in request.form:
        return render_template('app/registration/check-your-answers-uk-org.html',
                               error_title="There are errors on this page",
                               fields={'terms': {'data': '', 'error': ['You must agree with the terms of use']}})

    success = _register_user()

    if success:
        return redirect('/registration/confirmation-uk-organisation')
    else:
        return redirect('/error')


@registration_uk_organisation.route('/confirmation-uk-organisation', methods=['GET'])
def confirmation():
    return render_template('app/confirmation/index.html',
                           title="Application complete",
                           registration=True)


# - Helper functions - #

def _session_invalid(fields):
    return not in_session(fields, 'uk-organisation')


def _register_user():
    session, reg_obj = fetch_registration()
    ulapd_api = UlapdAPI()

    current_app.logger.info("!!!!!: " + str(reg_obj))

    data_dict = {
        'user_type': 'organisation-uk',
        'email': reg_obj['email'],
        'title': reg_obj['title'],
        'first_name': reg_obj['first_name'],
        'last_name': reg_obj['last_name'],
        'contact_preferences': reg_obj.get('contact_preferences', []),
        'telephone_number': reg_obj['uk_org_phone'],
        'organisation_name': reg_obj['uk_org_name'],
        'organisation_type': reg_obj['uk_org_type'],
        'registration_number': reg_obj.get('uk_org_reg_no', None),
        'address_line_1': reg_obj['uk_org_street_line_1'],
        'address_line_2': reg_obj['uk_org_street_line_2'],
        'city': reg_obj['uk_org_city'],
        'county': reg_obj['uk_org_county'],
        'postcode': reg_obj['uk_org_postcode'],
        'country': 'UK'
    }

    print(data_dict)

    user_response = ulapd_api.create_user(data_dict)
    session.pop('registration', None)
    dps_session.commit()
    return user_response


def _add_org_type_validators(dto):
    form = FormValidator("There are errors on this page")
    form.add_validator('type', dto.type, org_type_validator)
    return form
