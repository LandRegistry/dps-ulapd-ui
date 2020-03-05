from flask import current_app
from ulapd_ui.utils.session import dps_session
from ulapd_ui.utils.validation import FormValidator, is_not_empty, email_validator, phone_number_validator, \
    postcode_validator, crn_validator, account_exists, is_overseas_country
from ulapd_ui.dependencies.gov_pay import request_payment, get_payment_status
from ulapd_ui.utils.registration_data import get_verification_details


def fetch_registration():
    session = dps_session.get_state()
    reg_obj = None
    if 'registration' in session:
        reg_obj = session['registration']

    return session, reg_obj


def in_session(fields, journey):
    """This method checks if cetain data is present in the registration object,
    this can be user to check if the user has completed the previous steps
    This method can take a string or a list of strings
    """
    _, reg_obj = fetch_registration()
    if reg_obj is None:
        return False

    try:
        if reg_obj['user_type'] != journey:
            return False
    except KeyError:
        return False
    fields_list = fields
    # Deal with single input rather than a list
    if not isinstance(fields, list):
        fields_list = [fields]

    for field in fields_list:
        if field not in reg_obj:
            return False

    return True


def add_personal_info_validators(dto, user_type=None):
    form = FormValidator('There are errors on this page')
    form.add_validator('title', dto.title, fvs=is_not_empty, empty_msg='Enter your title')
    form.add_validator('first_name', dto.first_name, fvs=is_not_empty, empty_msg='Enter your first name')
    form.add_validator('last_name', dto.last_name, fvs=is_not_empty, empty_msg='Enter your last name')
    form.add_validator('email', dto.email, fvs=[is_not_empty, email_validator, account_exists],
                       empty_msg='Enter your email')
    if user_type != 'org':
        form.add_validator('phone',
                           dto.phone,
                           fvs=[is_not_empty, phone_number_validator],
                           empty_msg='Enter your phone number')
    return form


def add_org_info_validators(dto, bypass):
    form = FormValidator('There are errors on this page')

    if bypass is False:
        form.add_validator('name', dto.name, is_not_empty, empty_msg='Enter your organisation name')
    form.add_validator('building_and_street', dto.street_line_1, is_not_empty, empty_msg='Enter a building and street')
    form.add_validator('street_line_1', dto.street_line_1, [], empty_msg='Enter a building and street')
    form.add_validator('street_line_2', dto.street_line_2)
    form.add_validator('city', dto.city, is_not_empty, empty_msg='Enter a town or city')
    form.add_validator('county', dto.county, is_not_empty, empty_msg='Enter a county')
    form.add_validator('postcode', dto.postcode, fvs=[is_not_empty, postcode_validator],
                       empty_msg='Enter your postcode')
    form.add_validator('phone', dto.phone, fvs=[is_not_empty, phone_number_validator],
                       empty_msg='Enter your phone number')
    return form


def add_overseas_info_validators(dto):
    form = FormValidator('There are errors on this page')
    form.add_validator('name', dto.name, is_not_empty, empty_msg='Enter your organisation name')
    form.add_validator('country', dto.country_incorp, [is_not_empty, is_overseas_country], empty_msg='Enter a country')
    return form


def add_company_details_validators(dto):
    form = FormValidator('There are errors on this page')

    form.add_validator('name', dto.name, is_not_empty, empty_msg='Enter your company name')
    form.add_validator('reg_no', dto.reg_no, [is_not_empty, crn_validator],
                       empty_msg='Enter your company registration number')
    return form


def add_charity_details_validators(dto):
    form = FormValidator('There are errors on this page')

    form.add_validator('name', dto.name, is_not_empty, empty_msg='Enter your charity name')
    form.add_validator('charity', dto.reg_no, [is_not_empty],
                       empty_msg='Enter your charity number')
    return form


def add_org_address_validators(dto, org):
    form = FormValidator('There are errors on this page')
    form.add_validator('building_and_street', dto.street_line_1, is_not_empty, empty_msg='Enter a building and street')
    form.add_validator('street_line_1', dto.street_line_1, [], empty_msg='Enter a building and street')
    form.add_validator('street_line_2', dto.street_line_2)
    form.add_validator('city', dto.city, is_not_empty, empty_msg='Enter a town or city')
    form.add_validator('phone', dto.phone, fvs=[is_not_empty, phone_number_validator],
                       empty_msg='Enter your phone number')
    if org == 'overseas':
        msg = 'Enter a country'
        form.add_validator('country', dto.country, [is_not_empty], empty_msg=msg)
        form.add_validator('postcode', dto.postcode, fvs=[], empty_msg='')
    else:
        form.add_validator('county', dto.county, is_not_empty, empty_msg='Enter a county')
    return form


def populate_session(dto, prefix=None):
    session = dps_session.get_state()
    for name, value in dto._asdict().items():
        full_name = name if prefix is None else (prefix + name)
        actual_value = '' if value is None else value
        session['registration'][full_name] = actual_value
    return session


def begin_verification():
    current_app.logger.info('Verifying user')
    session, reg_obj = fetch_registration()
    reference = 'HMLR Data Publication'
    response = request_payment(0, reference, 'Use land and property data', reg_obj['user_type'])

    if response is None:
        current_app.logger.error('GovPay failure')
        return '/error'

    verification_details = get_verification_details(response)
    session['registration']['verification_details'] = verification_details
    dps_session.commit()

    return verification_details.next_url


def complete_verification(verification_id):
    current_app.logger.info('Completing user verification')

    response = get_payment_status(verification_id)
    return response


# - Helper functions - #


def is_hmlr_email(email):
    return True if 'landregistry.gov.uk' in email or 'digital.landregistry.gov.uk' in email else False


def amend_session_user_type(user_type):
    session = dps_session.get_state()
    session['registration']['user_type'] = user_type
    return session
