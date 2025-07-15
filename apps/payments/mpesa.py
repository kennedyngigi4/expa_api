import requests
import base64
import json
from requests.auth import HTTPBasicAuth 
from datetime import datetime


class MPESA:

    def __init__(self, phone, amount):
        self.consumer_key = "CoekQiy5PmUdgRJtRKyCoV9WB3pMWj6cabG1lWP2H6XllhHB"
        self.consumer_secret = "sksJnGakoPJdNFFuoLsXbs7AyLCVFpyAQ9SrspTdG6EzeIVvANFTjwtYCjuoNdlk"
        self.authorization_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        self.phone = phone
        self.amount = round(float(amount))



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
        request = {
            "BusinessShortCode": self.LipaNow()['business_short_code'],
            "Password": self.LipaNow()['decode_password'],
            "Timestamp": self.LipaNow()['lipa_time'],
            "TransactionType": "CustomerBuyGoodsOnline",
            "Amount": self.amount,
            "PartyA": self.phone,  # replace with your phone number to get stk push
            "PartyB": self.LipaNow()['business_short_code'],
            "PhoneNumber": self.phone,  # replace with your phone number to get stk push
            "CallBackURL": "https://expa.co.ke/stk_callback",
            "AccountReference": "EXPA Logistics",
            "TransactionDesc": "EXPA Logistics"
        }
        response = requests.post(api_url, json=request, headers=headers)
        return response
