from flask import render_template, redirect, request, Blueprint
from ulapd_ui.utils.registration_utilities import fetch_registration, populate_session
from ulapd_ui.utils.registration_data import collect_research, collect_preferences
from ulapd_ui.utils.validation import FormValidator, research_validator, preference_validator
from ulapd_ui.utils.session import dps_session

registration = Blueprint('registration', __name__, url_prefix="/registration")

user_flow = {
    'personal': '/registration/about-you-personal',
    'uk-organisation': '/registration/about-you-uk-organisation',
    'overseas-organisation': '/registration/about-you-overseas-organisation'
}


@registration.route('', methods=['GET'])
def user_type():
    _, reg_obj = fetch_registration()
    breadcrumb_links = [{"label": "Home", "href": "/"},
                        {"label": "Create an account", "href": None}]
    return render_template("app/registration/user_type.html", errors=False, registration=reg_obj,
                           breadcrumb_links=breadcrumb_links)


@registration.route('', methods=['POST'])
def submit_user_type():
    session, reg_obj = fetch_registration()
    if "user_type" not in request.form:
        return render_template("app/registration/user_type.html", errors=True, registration=reg_obj)
    else:
        # Create the registration object if it doesn't exist
        if 'registration' not in session:
            session['registration'] = {}
        session['registration']['user_type'] = request.form['user_type']
        session['registration']['ip_address'] = request.remote_addr
        if 'changing_answers' in session['registration']:
            session['registration']['changing_answers'] = False
        dps_session.commit()
        return redirect(user_flow[request.form["user_type"]])


@registration.route('/research', methods=['GET'])
def get_research_page():
    return render_template('app/registration/research.html')


@registration.route('/research', methods=['POST'])
def submit_research():

    research_info = collect_research(request.form)
    form = _add_research_validators(research_info)

    if form.is_valid():
        session = populate_session(research_info)
        dps_session.commit()
        if research_info.research == 'yes':
            return redirect('/registration/contact-preferences')
        else:
            session['registration']['changing_answers'] = True
            dps_session.commit()
            if request.form['user_type'] == 'overseas-organisation':
                return redirect('/registration/check-your-answers-overseas-organisation')
            elif request.form['user_type'] == 'uk-organisation':
                return redirect('/registration/check-your-answers-uk-organisation')
            else:
                return redirect('/registration/check-your-answers-personal')

    else:
        return render_template('app/registration/research.html',
                               error_title="There are errors on this page",
                               fields=form.validate())


@registration.route('/contact-preferences', methods=['GET'])
def get_contact_preferences_page():
    return render_template('app/registration/contact_preferences.html')


@registration.route('/contact-preferences', methods=['POST'])
def submit_contact_preferences():

    preferences = request.form.getlist('preferences')
    preference_info = collect_preferences(request.form)
    form = _add_preference_validators(preferences)

    if form.is_valid():
        session = populate_session(preference_info)
        session['registration']['contact_preferences'] = preferences
        session['registration']['changing_answers'] = True
        dps_session.commit()
        if request.form['user_type'] == 'overseas-organisation':
            return redirect('/registration/check-your-answers-overseas-organisation')
        elif request.form['user_type'] == 'uk-organisation':
            return redirect('/registration/check-your-answers-uk-organisation')
        else:
            return redirect('/registration/check-your-answers-personal')
    else:
        return render_template('app/registration/contact_preferences.html',
                               error_title="There are errors on this page",
                               fields=form.validate())


def _add_research_validators(dto):
    form = FormValidator("There are errors on this page")
    form.add_validator('research', dto.research, research_validator)
    return form


def _add_preference_validators(pref_list):
    form = FormValidator("There are errors on this page")
    form.add_validator('preferences', pref_list, preference_validator)
    return form
