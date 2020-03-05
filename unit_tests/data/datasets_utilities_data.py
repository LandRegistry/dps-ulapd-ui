session_data = {
    'user': {
        'datasets': {
            'ccod': {
                'date_agreed': 'Mon, 18 Nov 2019 14:43:05 GMT',
                'private': False,
                'valid_licence': True
            },
            'ocod': {
                'date_agreed': 'Tue, 19 Nov 2019 14:43:05 GMT',
                'private': False,
                'valid_licence': False
            },
            'nps': {
                'date_agreed': None,
                'private': True,
                'valid_licence': True
            }
        },
        'user_details': {
            'address_line_1': '12',
            'address_line_2': 'Road',
            'api_key': 'c1dc7bf0-4241-428f-aec2-ef4be5e2f34a',
            'city': 'Plymouth',
            'contactable': True,
            'country': 'UK',
            'country_of_incorporation': None,
            'county': 'Devon',
            'date_added': '2019-11-18 10:48:51.773390',
            'email': 'spuu@fakermail.com',
            'first_name': 'Ted',
            'last_name': 'Jones',
            'ldap_id': 'c624b255-da03-471a-8f1d-d26422650845',
            'organisation_name': None,
            'organisation_type': None,
            'postcode': 'PL1 1AA',
            'registration_number': None,
            'telephone_number': '01232323232332',
            'title': 'Mr',
            'user_details_id': 1,
            'user_type': {
                    'date_added': 'Mon, 18 Nov 2019 08:02:00 GMT',
                    'user_type': 'personal-uk',
                    'user_type_id': 1
            },
            'user_type_id': 1
        }
    }
}

get_latest_download_activities_input = [
    {
        'dataset_id': 'ocod',
        'timestamp': 'Thu, 21 Nov 2019 14:17:08 GMT'
    },
    {
        'dataset_id': 'nps_sample',
        'timestamp': 'Mon, 25 Nov 2019 16:30:51 GMT'
    },
    {
        'dataset_id': 'ccod',
        'timestamp': 'Thu, 21 Nov 2019 14:16:45 GMT'
    },
    {
        'dataset_id': 'ccod',
        'timestamp': 'Thu, 21 Nov 2019 11:09:07 GMT'
    }
]


get_latest_download_activities_expected = [
    {
        'dataset_id': 'ocod',
        'timestamp': 'Thu, 21 Nov 2019 14:17:08 GMT'
    },
    {
        'dataset_id': 'nps_sample',
        'timestamp': 'Mon, 25 Nov 2019 16:30:51 GMT'
    },
    {
        'dataset_id': 'ccod',
        'timestamp': 'Thu, 21 Nov 2019 14:16:45 GMT'
    }
]


build_download_history_activites = [
    {
        'dataset_id': 'ocod',
        'timestamp': 'Thu, 21 Nov 2019 14:17:08 GMT'
    },
    {
        'dataset_id': 'ccod',
        'timestamp': 'Mon, 25 Nov 2019 16:30:51 GMT'
    },
    {
        'dataset_id': 'nps',
        'timestamp': 'Wed, 27 Nov 2019 16:30:51 GMT'
    }
]


build_download_history_expected = [
    {
        'dataset_id': 'ocod',
        'dataset_title': 'ocod',
        'last_download_date': '21 November 2019',
        'last_update_date': '07 November 2019',
        'licence_exists': 'ocod',
        'is_latest_download': True,
        'licence_agree_date': '19 November 2019',
        'is_licence_agreed': True,
        'resources': []
    },
    {
        'dataset_id': 'ccod',
        'dataset_title': 'ccod',
        'last_download_date': '25 November 2019',
        'last_update_date': '30 November 2019',
        'licence_exists': 'ccod',
        'is_latest_download': False,
        'licence_agree_date': '18 November 2019',
        'is_licence_agreed': True,
        'resources': []
    },
    {
        'dataset_id': 'nps',
        'dataset_title': 'nps',
        'last_download_date': '27 November 2019',
        'last_update_date': '30 November 2019',
        'licence_exists': None,
        'is_latest_download': False,
        'licence_agree_date': None,
        'is_licence_agreed': True,
        'resources': []
    }
]
