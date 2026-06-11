# views.py

import base64
import requests
import os
from datetime import datetime

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from .models import MpesaPayment
from rest_framework.permissions import IsAuthenticated
from accounts.models import Wallet
from accounts.models import Activate


class STKPushView(APIView):
    """
    Initiate STK Push
    """

    def post(self, request):

        try:
            # 1️⃣ Validate input
            phone_number = request.data.get("number")
            amount = request.data.get("amount")

            if not phone_number or not amount:
                return Response(
                    {"error": "Phone number and amount are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not str(phone_number).startswith("254"):
                return Response(
                    {"error": "Phone number must start with 254"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if int(amount) < 500:
                return Response(
                    {"error": "Amount must be greater than 500"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 2️⃣ M-Pesa Config (Use environment variables in production)
            business_shortcode = "174379"
            passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
            consumer_key = "eSQFZduKSQDj680euPXR4huvjcpfYJkWsbAK6T4dOAVsTNA8"
            consumer_secret = "pBPwGPOxtmB9fvu8vhc1Y4slVZAuG5ROgKPys9GrhKLcw9iGGcs77xpFJYLRM3nM"

            callback_url = "https://carmelia-hyperscholastic-uneugenically.ngrok-free.dev/mpesa/callback/"

            # 3️⃣ Generate Timestamp
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            # 4️⃣ Generate Password
            data_to_encode = business_shortcode + passkey + timestamp
            password = base64.b64encode(
                data_to_encode.encode()
            ).decode()

            # 5️⃣ Generate Access Token
            auth_string = f"{consumer_key}:{consumer_secret}"
            encoded_auth = base64.b64encode(
                auth_string.encode()
            ).decode()

            token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

            token_headers = {
                "Authorization": f"Basic {encoded_auth}"
            }

            token_response = requests.get(token_url, headers=token_headers)

            if token_response.status_code != 200:
                return Response(
                    {"error": "Failed to get access token"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            access_token = token_response.json().get("access_token")

            if not access_token:
                return Response(
                    {"error": "Access token missing"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # 6️⃣ Prepare STK Payload
            stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "BusinessShortCode": business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone_number,
                "PartyB": business_shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": callback_url,
                "AccountReference": "Test123",
                "TransactionDesc": "Payment Test"
            }

            response = requests.post(stk_url, json=payload, headers=headers)

            if response.status_code != 200:
                return Response(
                    {"error": "STK request failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            response_data = response.json()

            # 7️⃣ Handle Daraja Immediate Errors
            if response_data.get("ResponseCode") != "0":
                return Response(
                    {
                        "error": "STK push not accepted",
                        "details": response_data
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {
                    "message": "STK push sent successfully",
                    "data": response_data
                },
                status=status.HTTP_200_OK
            )

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": "Network error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except ValueError:
            return Response(
                {"error": "Invalid amount format"},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {"error": "Something went wrong", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MpesaCallbackView(APIView):
    """
    Handle M-Pesa Callback
    """

    authentication_classes = []
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            data = request.data

            body = data.get("Body", {}).get("stkCallback", {})

            result_code = body.get("ResultCode")
            result_desc = body.get("ResultDesc")
            checkout_id = body.get("CheckoutRequestID")

            metadata = body.get("CallbackMetadata", {}).get("Item", [])

            metadata_dict = {
                item.get("Name"): item.get("Value")
                for item in metadata
            }

            amount = metadata_dict.get("Amount")
            receipt = metadata_dict.get("MpesaReceiptNumber")
            phone = metadata_dict.get("PhoneNumber")
            trans_date = metadata_dict.get("TransactionDate")

            if result_code == 0:
                MpesaPayment.objects.create(
                    amount=amount,
                    receipt=receipt,
                    phone=phone,
                    date=trans_date,
                    checkout_id=checkout_id,
                    result_code=result_code,
                    result_desc=result_desc
                )
                
                Wallet.balance += amount

            return Response(
                {"message": "Callback received",
                 "status": "Activated"
                 },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": "Callback processing failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )