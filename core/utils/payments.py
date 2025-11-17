import requests
from django.conf import settings


class NobukPayments():
    api_url = "https://api.nobuk.africa"

    def __init__(self, user_phone=None, user_name=None, order_id=None, amount=None, source=None, withdrawal_amount=None, withdrawal_id=None, rider_phone=None, rider_name=None):

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


        # Rider withdrawal details
        self.withdrawal_amount = withdrawal_amount
        self.withdrawal_id = withdrawal_id
        self.rider_phone = rider_phone
        self.rider_name = rider_name


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



    def Withdrawal(self):
        if not all([self.withdrawal_amount, self.withdrawal_id, self.rider_phone, self.rider_name]):
            raise ValueError("Missing required withdrawal fields")
    
        headers = {
            "Content-Type": "application/json",
            "org": self.org_id,
            "apikey": self.api_key,
        }

        #payload
        payload = {
            "account": "EX Parcel Limited",
            "amount": str(self.withdrawal_amount),
            "request_id": str(self.withdrawal_id),
            "msisdn": self.rider_phone,
            "payment_reason": f"Rider Fees by {self.rider_name}"
        }


        try:
            response = requests.post(
                "https://lipia.nobuk.africa/b2c/initiate",
                json=payload,
                headers=headers
            )

            return response
        except requests.exceptions.RequestException as e:
            print("Request failed: ", e)