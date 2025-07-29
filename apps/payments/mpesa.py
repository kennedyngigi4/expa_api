import requests
import base64
import json
from requests.auth import HTTPBasicAuth 
from datetime import datetime


class MPESA:

    def __init__(self, phone, amount):
        self.consumer_key = "3rsVbkLos9UaFQ3ervHvSOaNiXrbPG1CcmSoDp4G4VE41SsM"
        self.consumer_secret = "gygGBnZwbAPbU0lulH8UxGoDI0hS1GcMaGep6J60QAWLySplcGkmzf9hRDDWiFYi"
        self.authorization_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        self.phone = phone
        self.amount = amount



    def generateCredentials(self):
        
        auth = requests.get(self.authorization_url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret))
        response = json.loads(auth.text)
        
        access_token = response["access_token"]
        return access_token


    def LipaNow(self):
        lipa_time = datetime.now().strftime("%Y%m%d%H%M%S")
        business_short_code = "174379"
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        data_to_encode = business_short_code + passkey + lipa_time
        online_password = base64.b64encode(data_to_encode.encode())
        decode_password = online_password.decode("utf-8")

        context = {
            "lipa_time": lipa_time,
            "business_short_code": business_short_code,
            "decode_password": decode_password
        }

        return context
    
    
    def MpesaSTKPush(self):
        access_token = self.generateCredentials()
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        lipa_context = self.LipaNow()
        request = {
            "BusinessShortCode": lipa_context['business_short_code'],
            "Password": lipa_context['decode_password'],
            "Timestamp": lipa_context['lipa_time'],
            "TransactionType": "CustomerPayBillOnline",
            "Amount": self.amount,
            "PartyA": self.phone,  # replace with your phone number to get stk push
            "PartyB": lipa_context['business_short_code'],
            "PhoneNumber": self.phone,  # replace with your phone number to get stk push
            "CallBackURL": "https://expa.co.ke",
            "AccountReference": "EXPA Logistics",
            "TransactionDesc": "EXPA Logistics"
        }
        response = requests.post(api_url, json=request, headers=headers)
        return response
