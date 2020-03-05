from datetime import datetime
from flask import render_template, redirect, request, Blueprint, url_for
from ulapd_ui.utils.session import dps_session
from ulapd_ui.dependencies.ulapd_api import UlapdAPI
from ulapd_ui.utils.registration_utilities import in_session, add_personal_info_validators, \
    populate_session, fetch_registration, begin_verification, \
    complete_verification, is_hmlr_email, amend_session_user_type
from ulapd_ui.utils.registration_data import collect_personal_info, collect_address_type, collect_address
from ulapd_ui.utils.validation import FormValidator, is_not_empty, postcode_validator, residency_validator, \
     is_overseas_country


registration_personal = Blueprint('registration_personal', __name__, url_prefix="/registration")


@registration_personal.route('/about-you-personal', methods=['GET'])
def get_personal_info_page():
    if _session_invalid('user_type'):
        return redirect('/registration')

    return render_template('app/registration/personal_information.html', route='about-you-personal')


@registration_personal.route('/about-you-personal', methods=['POST'])
def submit_personal_info():
    if _session_invalid('user_type'):
        return redirect('/registration')

    personal_info = collect_personal_info(request.form)

    form = add_personal_info_validators(personal_info)

    if form.is_valid():
        session = populate_session(personal_info)
        dps_session.commit()
        # if user has HMLR email then they need to be directed to the uk org journey
        if is_hmlr_email(personal_info.email):
            return render_template('app/registration/personal_information.html',
                                   error_title="There are errors on this page",
                                   route='about-you-personal',
                                   fields={'hmlr_email': True,
                                           'name': 'email',
                                           'error': 'You cannot create a personal account using a HM Land Registry '
                                                    'email address',
                                           'link': '/registration/about-you-personal-redirect',
                                           'link_text': 'Create a UK organisation account'})
        else:
            if 'changing_answers' in session['registration']:
                return redirect('/registration/check-your-answers-personal')
            return redirect('/registration/address-type-personal')
    else:
        return render_template('app/registration/personal_information.html',
                               error_title="There are errors on this page",
                               route='about-you-personal',
                               fields=form.validate())


@registration_personal.route('/about-you-personal-redirect', methods=['GET'])
def redirect_journey():
    amend_session_user_type('uk-organisation')
    dps_session.commit()

    return redirect(url_for('registration_uk_organisation.get_personal_info_page'))


@registration_personal.route('/address-type-personal', methods=['GET'])
def get_address_page():
    if _session_invalid(['title']):
        return redirect('/registration/about-you-personal')

    return render_template('app/registration/address-type-personal.html')


@registration_personal.route('/address-type-personal', methods=['POST'])
def submit_address():
    if _session_invalid(['title']):
        return redirect('/registration/about-you-personal')

    address_type = collect_address_type(request.form)
    form = _add_address_type_validators(address_type)

    if form.is_valid():
        populate_session(address_type)
        dps_session.commit()
        return redirect('/registration/address-details-personal')
    else:
        return render_template('app/registration/address-type-personal.html',
                               error_title="There are errors on this page",
                               fields=form.validate())


@registration_personal.route('/address-details-personal', methods=['GET'])
def get_address_uk_page():
    if _session_invalid(['uk_resident']):
        return redirect('/registration/address-type-personal')

    return render_template('app/registration/address-details-personal.html')


@registration_personal.route('/address-details-personal', methods=['POST'])
def submit_address_uk():
    if _session_invalid(['uk_resident']):
        return redirect('/registration/address-type-personal')

    address_info = collect_address(request.form)
    form = _add_address_validators(address_info)

    if form.is_valid():
        session = populate_session(address_info)
        dps_session.commit()
        if 'changing_answers' in session['registration']:
            return redirect('/registration/check-your-answers-personal')
        return redirect('/registration/research')
    else:
        return render_template('app/registration/address-details-personal.html',
                               error_title="There are errors on this page",
                               fields=form.validate())


@registration_personal.route('/check-your-answers-personal', methods=['GET'])
def get_check_your_answers_page():
    if _session_invalid(['uk_resident', 'changing_answers']):
        return redirect('/registration/your-address-personal')

    return render_template('app/registration/check-your-answers-personal.html')


@registration_personal.route('/check-your-answers-personal', methods=['POST'])
def submit_answers():
    if _session_invalid(['uk_resident', 'changing_answers']):
        return redirect('/registration/your-address-personal')

    if 'terms' not in request.form:
        return render_template('app/registration/check-your-answers-personal.html',
                               error_title="There are errors on this page",
                               fields={'terms': {'data': '', 'error': ['You must agree with the terms of use']}})

    url = begin_verification()
    return redirect(url)


@registration_personal.route('/verification', methods=['GET'])
def handle_verification():
    if in_session('confirmed', journey=None):
        return redirect(url_for('registration_personal.confirmation'))

    if _session_invalid(['verification_details']):
        return redirect('app/registration/check-your-answers-personal')

    session, reg_obj = fetch_registration()
    # action = complete_verification(reg_obj['verification_details']['payment_id'])
    action = complete_verification(reg_obj['verification_details'][0])
    if action['state']['status'] in ['failed', 'error']:
        del session['registration']
        dps_session.commit()
        return redirect(url_for('general.get_list'))

    data_on_success = _register_user()
    if data_on_success:
        return redirect(url_for('registration_personal.confirmation'))
    else:
        return redirect('/error')


@registration_personal.route('/confirmation-personal', methods=['GET'])
def confirmation():
    return render_template('app/confirmation/index.html',
                           title="Application complete",
                           registration=True,
                           verified=True)


# - Helper functions - #

def _session_invalid(fields):
    return not in_session(fields, 'personal')


def _add_address_type_validators(dto):
    form = FormValidator("There are errors on this page")
    form.add_validator('uk_resident', dto.uk_resident, residency_validator)
    return form


def _add_address_validators(dto):
    form = FormValidator("There are errors on this page")
    if dto.uk_resident == 'yes':
        form.add_validator('postcode',
                           dto.postcode,
                           [is_not_empty, postcode_validator],
                           empty_msg="Enter your postcode")
        form.add_validator('county', dto.county, [is_not_empty], empty_msg="Enter your county")
    elif dto.uk_resident == 'no':
        form.add_validator('country', dto.country, [is_not_empty, is_overseas_country], empty_msg='Enter your country')
        form.add_validator('postcode', dto.postcode, fvs=[], empty_msg='')

    form.add_validator('building_and_street', dto.street_line_1, is_not_empty, empty_msg='Enter a building and street')
    form.add_validator('street_line_1', dto.street_line_1, [], empty_msg='Enter a building and street')
    form.add_validator('street_line_2', dto.street_line_2)
    form.add_validator('city', dto.city, is_not_empty, empty_msg='Enter a town or city')

    return form


def _register_user():
    session, reg_obj = fetch_registration()
    ulapd_api = UlapdAPI()

    user_type = 'personal-' + ('uk' if reg_obj['country'] == 'UK' else 'overseas')
    data_dict = {
        'user_type': user_type,
        'email': reg_obj['email'],
        'title': reg_obj['title'],
        'first_name': reg_obj['first_name'],
        'last_name': reg_obj['last_name'],
        # 'contactable': True if reg_obj['research'] == 'yes' else False,
        'contact_preferences': reg_obj.get('contact_preferences', []),
        'telephone_number': reg_obj['phone'],
        'address_line_1': reg_obj['street_line_1'],
        'address_line_2': reg_obj['street_line_2'],
        'city': reg_obj['city'],
        'postcode': reg_obj['postcode'],
        'county': reg_obj['county'],
        'country': reg_obj['country']
    }

    user_response = ulapd_api.create_user(data_dict)
    session.pop('registration', None)
    dps_session.commit()
    return user_response
