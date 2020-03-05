from flask import Blueprint, render_template, redirect, request, url_for
from datetime import datetime
from ulapd_ui.utils.registration_utilities import in_session, add_personal_info_validators, \
    populate_session, fetch_registration, begin_verification, \
    complete_verification, is_hmlr_email, add_org_address_validators, add_overseas_info_validators
from ulapd_ui.utils.registration_data import collect_personal_info, collect_overseas_org_info, \
    collect_overseas_org_address
from ulapd_ui.utils.session import dps_session
from ulapd_ui.dependencies.ulapd_api import UlapdAPI


registration_overseas_org = Blueprint('registration_overseas_org', __name__, url_prefix='/registration')


@registration_overseas_org.route('/about-you-overseas-organisation', methods=['GET'])
def get_personal_info_page():
    if _session_invalid('user_type'):
        return redirect('/registration')

    return render_template('app/registration/personal_information.html', route='about-you-overseas-organisation')


@registration_overseas_org.route('/about-you-overseas-organisation', methods=['POST'])
def submit_personal_info_page():
    if _session_invalid('user_type'):
        return redirect('/registration')

    personal_info = collect_personal_info(request.form, 'org')

    form = add_personal_info_validators(personal_info, 'org')

    if form.is_valid():
        session = populate_session(personal_info)
        dps_session.commit()

        # if user has HMLR email then they need to be directed to the uk org journey
        if is_hmlr_email(personal_info.email):
            return render_template('app/registration/personal_information.html',
                                   error_title="There are errors on this page",
                                   route='about-you-overseas-organisation',
                                   fields={'hmlr_email': True,
                                           'name': 'email',
                                           'error': 'You cannot create a overseas organisation account using '
                                                    'a HM Land Registry email address',
                                           'link': '/registration/about-you-overseas-organisation-redirect',
                                           'link_text': 'Create a UK organisation account'})
        else:
            if 'changing_answers' in session['registration']:
                return redirect('/registration/check-your-answers-overseas-organisation')
            return redirect('/registration/about-your-organisation-overseas')
    else:
        return render_template('app/registration/personal_information.html',
                               error_title="There are errors on this page",
                               route='about-you-overseas-organisation',
                               fields=form.validate())


@registration_overseas_org.route('/about-your-organisation-overseas', methods=['GET'])
def get_org_info_page():
    if _session_invalid(['title']):
        return redirect('/registration/about-you-overseas-organisation')

    return render_template('app/registration/org_information_overseas.html')


@registration_overseas_org.route('/about-your-organisation-overseas', methods=['POST'])
def submit_org_info():
    if _session_invalid(['title']):
        return redirect('/registration/about-you-overseas-organisation')

    org_info = collect_overseas_org_info(request.form)

    form = add_overseas_info_validators(org_info)

    if form.is_valid():
        session = populate_session(org_info, prefix='overseas_org_')
        dps_session.commit()
        if 'changing_answers' in session['registration']:
            return redirect('/registration/check-your-answers-overseas-organisation')
        return redirect('/registration/about-your-organisation-address-overseas')
    else:
        return render_template('app/registration/org_information_overseas.html',
                               error_title="There are errors on this page",
                               fields=form.validate())


@registration_overseas_org.route('/about-your-organisation-address-overseas', methods=['GET'])
def get_org_address_page():
    if _session_invalid(['overseas_org_country_incorp']):
        return redirect('/registration/about-your-organisation-overseas')

    return render_template('app/registration/org_address_overseas.html')


@registration_overseas_org.route('/about-your-organisation-address-overseas', methods=['POST'])
def submit_org_address():
    if _session_invalid(['overseas_org_country_incorp']):
        return redirect('/registration/about-your-organisation-overseas')

    org_info = collect_overseas_org_address(request.form)

    form = add_org_address_validators(org_info, 'overseas')

    if form.is_valid():
        session = populate_session(org_info, prefix='overseas_org_')
        dps_session.commit()
        if 'changing_answers' in session['registration']:
            return redirect('/registration/check-your-answers-overseas-organisation')
        return redirect('/registration/research')
    else:
        return render_template('app/registration/org_address_overseas.html',
                               error_title="There are errors on this page",
                               fields=form.validate())


@registration_overseas_org.route('/check-your-answers-overseas-organisation', methods=['GET'])
def check_your_answers():
    if _session_invalid(['overseas_org_name', 'changing_answers']):
        return redirect('/registration/about-your-organisation-overseas')
    return render_template('app/registration/check-your-answers-overseas-org.html')


@registration_overseas_org.route('/check-your-answers-overseas-organisation', methods=['POST'])
def submit_answers():
    if _session_invalid(['overseas_org_name', 'changing_answers']):
        return redirect('/registration/about-your-organisation-overseas')

    if 'terms' not in request.form:
        return render_template('app/registration/check-your-answers-overseas-org.html',
                               error_title="There are errors on this page",
                               fields={'terms': {'data': '', 'error': ['You must agree with the terms of use']}})

    url = begin_verification()
    return redirect(url)


@registration_overseas_org.route('/verification-overseas', methods=['GET'])
def handle_verification_overseas():
    if in_session('confirmed', journey=None):
        return redirect('/registration/confirmation-overseas-organisation')

    if _session_invalid(['verification_details']):
        return redirect('/registration/check-your-answers-overseas-organisation')

    session, reg_obj = fetch_registration()
    # action = complete_verification(reg_obj['verification_details']['payment_id'])
    action = complete_verification(reg_obj['verification_details'][0])
    if action['state']['status'] in ['failed', 'error']:
        del session['registration']
        dps_session.commit()
        return redirect(url_for('general.get_list'))
    success = _register_user()
    if success:
        return redirect('/registration/confirmation-overseas-organisation')
    else:
        return redirect('/error')


@registration_overseas_org.route('/confirmation-overseas-organisation', methods=['GET'])
def confirmation():
    return render_template('app/confirmation/index.html',
                           title="Application complete",
                           registration=True,
                           verified=True)


# - Helper functions - #

def _session_invalid(fields):
    return not in_session(fields, 'overseas-organisation')


def _register_user():
    session, reg_obj = fetch_registration()
    ulapd_api = UlapdAPI()

    data_dict = {
        'user_type': 'organisation-overseas',
        'email': reg_obj['email'],
        'title': reg_obj['title'],
        'first_name': reg_obj['first_name'],
        'last_name': reg_obj['last_name'],
        'contact_preferences': reg_obj.get('contact_preferences', []),
        'telephone_number': reg_obj['overseas_org_phone'],
        'organisation_name': reg_obj['overseas_org_name'],
        'country_of_incorporation': reg_obj['overseas_org_country_incorp'],
        'country': reg_obj['overseas_org_country'],
        'address_line_1': reg_obj['overseas_org_street_line_1'],
        'address_line_2': reg_obj['overseas_org_street_line_2'],
        'city': reg_obj['overseas_org_city'],
        'postcode': reg_obj['overseas_org_postcode']
    }

    user_response = ulapd_api.create_user(data_dict)
    session.pop('registration', None)
    dps_session.commit()
    return user_response
