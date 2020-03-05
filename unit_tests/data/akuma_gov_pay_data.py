gov_pay_data = {
    "payment_id": "1234567890",
    "provider_id": "1234567890",
    "description": "Data Publication Service verification",
    "language": "en",
    "return_url": "http://openresty:8080/registration/verification",
    "state": {
        "status": "success",
        "finished": True
    },
    "card_details": {
        "billing_address": {
            "city": "Auckland",
            "country": "GB",
            "line2": "Tui Street",
            "line1": "12",
            "postcode": "PL1 1AA"
        },
        "first_digits_card_number": "444433",
        "card_type": None,
        "cardholder_name": "sahdkjsahd",
        "expiry_date": "09/20",
        "card_brand": "Visa",
        "last_digits_card_number": "1111"
    },
    "amount": 0,
    "card_brand": "Visa",
    "_links": {
        "self": {
            "href": "https://publicapi.payments.service.gov.uk/v1/payments/1234567890",
            "method": "GET"
        },
        "events": {
            "href": "https://publicapi.payments.service.gov.uk/v1/payments/1234567890/events",
            "method": "GET"
        },
        "refunds": {
            "href": "https://publicapi.payments.service.gov.uk/v1/payments/1234567890/refunds",
            "method": "GET"
        }
    },
    "refund_summary": {
        "status": "full",
        "amount_submitted": 0,
        "amount_available": 0
    },
    "settlement_summary": {
        "capture_submit_time": "2019-08-13T13:01:58.899Z",
        "captured_date": "2019-08-13"
    },
    "created_date": "2019-08-13T13:00:22.093Z",
    "delayed_capture": False,
    "payment_provider": "sandbox",
    "email": "gharris@fakemail.com",
    "reference": "HMLR Data Publication"
}
