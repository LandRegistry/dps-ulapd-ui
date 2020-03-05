from collections import namedtuple

PersonalInfo = namedtuple('PersonalInfo',
                          'title, first_name, last_name, email, phone')
OrgPersonalInfo = namedtuple('OrgPersonalInfo',
                             'title, first_name, last_name, email')
AddressType = namedtuple('AddressType',
                         'uk_resident')
Address = namedtuple('Address',
                     'uk_resident, postcode, country, street_line_1, street_line_2, city, county')
OrganisationType = namedtuple('OrganisationType',
                              'type')
OrganisationInfo = namedtuple('OrganisationInfo',
                              'name, street_line_1, street_line_2, city, county, postcode, phone, type')
OrganisationInfo2 = namedtuple('OrganisationInfo2',
                               'street_line_1, street_line_2, city, county, postcode, phone, type')
OverseasOrgInfo = namedtuple('OverseasOrgInfo',
                             'name, country_incorp')
OverseasOrgAddress = namedtuple('OverseasOrgAddress',
                                ' street_line_1, street_line_2, city, postcode, country, phone')
VerificationState = namedtuple('VerificationState',
                               'payment_id, description, status, reference, next_url')
Research = namedtuple('Research', 'research')
Preferences = namedtuple('Preferences', 'telephone_pref, email_pref, post_pref')
CharityDetails = namedtuple('CharityDetails', 'name, reg_no')
CompanyDetails = namedtuple('CompanyDetails', 'name, reg_no')


def collect_personal_info(form, user_type=None):
    if user_type == 'org':
        return OrgPersonalInfo(form['title'].strip(),
                               form['first_name'].strip(),
                               form['last_name'].strip(),
                               form['email'].strip())
    else:
        return PersonalInfo(form['title'].strip(),
                            form['first_name'].strip(),
                            form['last_name'].strip(),
                            form['email'].strip(),
                            form['phone'].strip())


def collect_address_type(form):
    if 'uk_resident' not in form:
        uk_resident = None
    else:
        uk_resident = form['uk_resident']

    return AddressType(uk_resident)


def collect_address(form):
    if 'uk_resident' not in form:
        uk_resident = None
    else:
        uk_resident = form['uk_resident'].strip()

    street_line_1 = form['street_line_1'].strip()
    street_line_2 = form['street_line_2'].strip()
    city = form['city'].strip()

    postcode = None
    country = None
    county = None

    if uk_resident is not None:
        if uk_resident == 'yes':
            postcode = form['postcode'].strip()
            county = form['county'].strip()
            country = 'UK'
        elif uk_resident == 'no':
            country = form['country'].strip()
            postcode = form['postcode'].strip()

    return Address(uk_resident, postcode, country, street_line_1, street_line_2, city, county)


def collect_organisation_type(form):
    if 'type' not in form:
        type = None
    else:
        type = form['type']

    return OrganisationType(type)


def collect_organisation_info(form):

    name = form.get('name', '').strip()
    street_line_1 = form['street_line_1'].strip()
    street_line_2 = form['street_line_2'].strip()
    city = form['city'].strip()
    county = form['county'].strip()
    postcode = form['postcode'].strip()
    phone = form['phone'].strip()
    type = form['type'].strip()

    if form.get('type') == 'Charity' or form.get('type') == 'Company':
        return OrganisationInfo2(street_line_1, street_line_2, city, county, postcode, phone, type)
    return OrganisationInfo(name, street_line_1, street_line_2, city, county, postcode, phone, type)


def collect_charity_details(form):

    name = form['name'].strip()
    reg_no = form['charity'].strip()

    return CharityDetails(name, reg_no)


def collect_company_details(form):

    name = form['name'].strip()
    reg_no = form['reg_no'].strip()

    return CompanyDetails(name, reg_no)


def collect_overseas_org_info(form):
    return OverseasOrgInfo(form['name'].strip(),
                           form['country'].strip())


def collect_overseas_org_address(form):
    street_line_1 = form['street_line_1'].strip()
    street_line_2 = form['street_line_2'].strip()
    city = form['city'].strip()
    postcode = None if form['postcode'].strip() == '' else form['postcode'].strip()
    country = form['country'].strip()
    phone = form['phone'].strip()
    return OverseasOrgAddress(street_line_1, street_line_2, city, postcode, country, phone)


def get_verification_details(response):
    payment_id = response['payment_id'] if 'payment_id' in response else None
    description = response['description'] if 'description' in response else None
    reference = response['reference'] if 'reference' in response else None
    try:
        status = response['state']['status'] if 'state' in response else None
    except KeyError:
        status = None

    if response['_links']['next_url'] is not None:
        try:
            next_url = response['_links']['next_url']['href']
        except KeyError:
            next_url = None
    else:
        next_url = None

    return VerificationState(payment_id, description, status, reference, next_url)


def collect_research(form):
    if 'research' not in form:
        research = None
    else:
        research = form['research']

    return Research(research)


def collect_preferences(form):

    preferences = form.getlist('preferences')

    if not preferences:
        telephone = None
        email = None
        post = None
    else:
        telephone = False
        email = False
        post = False
        for preference in preferences:
            if preference == 'Telephone':
                telephone = True
            if preference == 'Email':
                email = True
            if preference == 'Post':
                post = True

    return Preferences(telephone, email, post)
