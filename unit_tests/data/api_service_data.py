get_datasets_return = [
    {
        "name": "ccod",
        "title": "UK companies that own property in England and Wales",
        "type": "licenced",
        "resources": []
    },
    {
        "name": "ocod",
        "title": "Overseas companies that own property in England and Wales",
        "type": "licenced",
        "resources": []
    },
    {
        "name": "nps",
        "title": "National Polygon Service",
        "type": "licenced",
        "resources": []
    },
    {
        "name": "nps_sample",
        "title": "National Polygon Service Sample",
        "type": "licenced",
        "resources": []
    },
    {
        "name": "rfi",
        "title": "Request for information (requisition) data",
        "type": "open",
        "resources": []
    }
]

get_api_datasets_expected = {
    'success': True,
    'result': [
        {
            "name": "ccod",
            "title": "UK companies that own property in England and Wales"
        },
        {
            "name": "ocod",
            "title": "Overseas companies that own property in England and Wales"
        },
        {
            "name": "nps",
            "title": "National Polygon Service"
        },
        {
            "name": "nps_sample",
            "title": "National Polygon Service Sample"
        }
    ]
}

user_details_with_agreements = {
    'datasets': {
        'ocod': {
            'private': False,
            'valid_licence': True,
            'date_agreed': '27 Nov 2019'
        },
        'ccod': {
            'private': False,
            'valid_licence': False,
            'date_agreed': '27 Nov 2019'
        },
        'nps': {
            'private': True,
            'valid_licence': True,
            'date_agreed': None
        }
    },
    'user_details': {
        'user_details_id': 1,
        'email': 'a@a.com'
    }
}

user_details_no_agreements = {
    'datasets': {}
}

get_dataset_by_name = {
    'ccod': {
        'private': False,
        'resources': [
            {
                'file_name': 'CCOD_FULL.CSV'
            }
        ]
    },
    'ocod': {
        'private': False,
        'resources': [
            {
                'file_name': 'OCOD_FULL.CSV'
            }
        ]
    },
    'nps': {
        'private': True,
        'resources': [
            {
                'file_name': 'NPS_FULL.CSV'
            }
        ]
    },
}
