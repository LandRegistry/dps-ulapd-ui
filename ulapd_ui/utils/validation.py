import string
import json
import re
from collections import namedtuple, OrderedDict
from ulapd_ui.dependencies.api import api_get


ValidationResult = namedtuple('ValidationResult', 'field_no, data, error')


class FormValidator():

    def __init__(self, default_error):
        self.fields = {}
        self.default_error = default_error
        self.field_no = 0

    def add_validator(
            self,
            field_name,
            data,
            fvs=lambda x, _: x,
            empty_msg=None):
        if field_name not in self.fields:
            self.fields[field_name] = {
                'field_no': self.field_no,
                'data': data,
                'empty_msg': empty_msg,
                'validators': []
            }
            self.field_no += 1

        if isinstance(fvs, list):
            for fv in fvs:
                self.fields[field_name]['validators'].append(fv)
        else:
            self.fields[field_name]['validators'].append(fvs)

    def is_valid(self):
        return '#' in self.validate()

    def validate(self):
        results = {}
        validation_error = False
        for field in self.fields:
            data = self.fields[field]['data']
            error_list = []
            for validator in self.fields[field]['validators']:
                try:
                    validator(data, {'empty_msg': self.fields[field]['empty_msg']})
                except Exception as e:
                    validation_error = True
                    error_list.append(str(e))
                    if field != 'passwords':
                        break
                except Exception as e:
                    validation_error = True
                    msg = e
                    if 'message' in e:
                        msg = e.message
                    if msg == '[':
                        error_list.append(json.loads(e.message))
                    else:
                        error_list.append(e.message)
                    if field != 'passwords':
                        break
            if data is None:
                data = ''
            results[field] = ValidationResult(
                self.fields[field]['field_no'], data, error_list)
        if not validation_error:
            results['#'] = ValidationResult(0, None, [self.default_error])

        sorted_results = OrderedDict(sorted(results.items(), key=lambda x: x[1].field_no))
        return sorted_results


def is_not_empty(input, context):
    if input is None or input == '':
        if context['empty_msg'] is None:
            msg = 'The input cannot be empty'
        else:
            msg = context['empty_msg']
        raise Exception(msg)
    return input


def phone_number_validator(input, _):
    number = input.replace(' ', '')
    if len(number) < 10:
        raise Exception('Please enter a valid phone number')
    if len(number) > 15:
        raise Exception('Please enter a valid phone number')

    # The next line is removed to linting due to flake8 for python2 to python3 incompatibilities
    phone_regex = "^(\+)?([0-9]|\ |\(|\)|\-|\–)*$"  # noqa: W605 E999
    valid_phone = re.match(phone_regex, input, re.UNICODE)
    if valid_phone is None:
        raise Exception('Please enter a valid phone number')


def password_length(password, _):
    if not len(password) >= 8:
        raise Exception('Password must be at least 8 characters long')
    return password


def password_letters(password, _):
    if not (any(x.isupper() for x in password) and
            any(x.islower() for x in password)):
        raise Exception('Password must have at least one uppercase letter and one lowercase letter')
    return password


def password_number(password, _):
    if not any(x.isdigit() for x in password):
        raise Exception('Password must have at least one number')
    return password


def password_symbol(password, _):
    if not len(set(string.punctuation).intersection(password)) > 0:
        raise Exception('Password must have at least one symbol - for example, a question mark')
    return password


def confirm_passwords_match(passwords, _):
    if passwords[0] != passwords[1]:
        raise Exception('Passwords must be the same')
    return passwords[1]


def account_exists(email, _):
    # Email cannot already exist in LDAP (and thus the service)
    content, status = api_get('/api/account/users?cn={}'.format(email))
    if status != 404:
        if status == 200:
            raise Exception('Account for {} already exists'.format(email))
        else:
            raise Exception('Could not check email address, please re-try submission'.format(email))


def email_validator(email, _):

    if '*' in email:
        raise Exception('Email cannot contain an asterisk')

    # Must contain exactly one '@'.
    # Must contain at least one character before the '@'.
    # Must have a dot after the '@', and the dot must not be the next character after the '@' or the last character.
    # General Email Regex (RFC 5322 Official Standard) taken from https://emailregex.com/
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

    # Strip whitespace from email before matching: it is permitted  but only between double quotes.
    valid_email = re.match(email_regex, email.strip())

    if valid_email is None:
        raise Exception('Email {} is not a valid format'.format(email))


def postcode_validator(postcode, _):
    search_query = postcode.strip("' ").upper()

    # Regx taken from: https://en.wikipedia.org/wiki/Postcodes_in_the_United_Kingdom#Validation
    postcode_regex_check = '^(([A-Z]{1,2}[0-9][A-Z0-9]?|ASCN|STHL|TDCU|BBND|[BFS]IQQ|PCRN|TKCA) ?[0-9][A-Z]{2}' \
                           '|BFPO ?[0-9]{1,4}|(KY[0-9]|MSR|VG|AI)[ -]?[0-9]{4}|[A-Z]{2} ?[0-9]{2}|GE ?CX' \
                           '|GIR ?0A{2}|SAN ?TA1)$'

    valid_postcode = re.match(postcode_regex_check, search_query)
    if valid_postcode is None:
        raise Exception('Postcode not recognised')

    return postcode.rstrip()


def crn_validator(input, _):
    input_without_whitespace = input.replace(' ', '')
    if len(input_without_whitespace) < 8:
        raise Exception('Company registration number is too short')

    if len(input_without_whitespace) > 8:
        raise Exception('Company registration number is too long')

    is_valid = re.match(r'^[a-zA-Z0-9]*$', input_without_whitespace)
    if not is_valid:
        raise Exception('Company registration number not recognised')

    return input


def org_type_validator(input, _):
    acceptable_org_types = ['Company', 'Charity', 'Government', 'Local authority']
    if input is None or input not in acceptable_org_types:
        raise Exception('Choose 1 option')

    return input


def residency_validator(input, _):
    acceptable_residencies = ['yes', 'no']
    if input is None or input not in acceptable_residencies:
        raise Exception('Choose 1 option')

    return input


def research_validator(input, _):
    acceptable_research = ['yes', 'no']
    if input is None or input not in acceptable_research:
        raise Exception('Choose 1 option')

    return input


def preference_validator(input, _):
    if not input:
        raise Exception('Choose 1 option')

    return input


def is_overseas_country(input, _):
    unacceptable_countries = ['united kingdom', 'uk', 'wales', 'england', 'scotland', 'northern ireland', 'ni']
    input_lower = input.lower()
    if input_lower in unacceptable_countries:
        raise Exception('Enter an overseas country')

    return input
