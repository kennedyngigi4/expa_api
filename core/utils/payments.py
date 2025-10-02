import requests
from django.conf import settings


class NobukPayments():
    api_url = "https://api.nobuk.africa"

    def __init__(self, user_phone, user_name, order_id, amount, source):

        # Static org details
        self.api_key = settings.NOBUK_API_KEY
        self.paylink_id = settings.NOBUK_PAYLINK_ID
        self.org_id = settings.NOBUK_ORG_ID
        self.sale_trx_code = settings.NOBUK_SALE_TRX_CODE
        self.collection_id = settings.NOBUK_COLLECTION_ID
    
        # user details
        self.user_phone = user_phone
        self.user_name = user_name
        self.order_id = order_id
        self.amount = amount
        self.source = source


    def STKPush(self):

        headers = {
            "Content-Type": "application/json",
            "org": self.org_id,
            "apikey": self.api_key,
        }

        payload = {
            "paylink_id": self.paylink_id,
            "org_id": self.org_id,
            "sale_trx_code": self.sale_trx_code,
            "collection_id": self.collection_id,
            "pay_amount": self.amount,
            "pay_number": self.user_phone,
            "pay_name": self.user_name,
            "pay_details": self.order_id,
            "link_source": self.source,
        }

        try:

            request = requests.post(
                f"{self.api_url}/business/auto/stktrigger",
                json=payload,
                headers=headers
            )

            print("Status:", request.status_code)
            print("Response:", request.text)       

        except requests.exceptions.RequestException as e:
            print("Request failed: ", e)





