"""Implement MFA using Twilio SMS."""
import os
import time
from twilio.rest import Client
from pumpwood_communication.exceptions import PumpWoodException


def send_code(code: str, mfa_method):
    """
    Send MFA authenticatication code to stdout.

    Args:
        code [str]: MFA code.
        mfa_method: PumpwoodMFAMethod object.
    """
    APPLICATION_NAME = os.getenv("PUMPWOOD__MFA__APPLICATION_NAME", "Pumpwood")
    msg = "{application_name} MFA autorization code:\n{code}".format(
        application_name=APPLICATION_NAME, code=code)

    # Twilio authentication variables
    TWILIO_ACCOUNT_SID = os.getenv(
        "PUMPWOOD__MFA__TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv(
        "PUMPWOOD__MFA__TWILIO_AUTH_TOKEN")
    TWILIO_SENDER_PHONE_NUMBER = os.getenv(
        "PUMPWOOD__MFA__TWILIO_SENDER_PHONE_NUMBER")
    TWILIO_DELIVERY_TIMEOUT = int(os.getenv(
        "PUMPWOOD__MFA__TWILIO_DELIVERY_TIMEOUT", "10"))

    IS_TWILIO_ACCOUNT_SID = TWILIO_ACCOUNT_SID is None
    IS_TWILIO_AUTH_TOKEN = TWILIO_AUTH_TOKEN is None
    IS_TWILIO_SENDER_PHONE_NUMBER = TWILIO_SENDER_PHONE_NUMBER is None
    val_parameter = (
        IS_TWILIO_ACCOUNT_SID or IS_TWILIO_AUTH_TOKEN or
        IS_TWILIO_SENDER_PHONE_NUMBER)
    if val_parameter:
        msg = "SMS MFA backend was not configured"
        raise PumpWoodException(
            msg, payload={"mfa_code": "backend_not_configured"})

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    to_phone_number = mfa_method.mfa_parameter
    message = client.messages.create(
      to=to_phone_number, body=msg,
      from_=TWILIO_SENDER_PHONE_NUMBER)

    # Check if SMS was delivered to user, it will wait
    # PUMPWOOD__MFA__TWILIO_DELIVERY_TIMEOUT 1 second sleep cicle for SMS
    # to be considered delivered.
    i = 0
    while True:
        message = message.fetch()
        if message.status == 'failed':
            msg = "MFA Twilio SMS received a 'failed' status"
            raise PumpWoodException(
                msg, payload={"mfa_code": "failed_status"})

        if TWILIO_DELIVERY_TIMEOUT <= i:
            msg = (
                "Waited for {} seconds and message did not receive "
                "'delivered' status. It is possible to use the MFA code for "
                "login, but we just gave up waiting for it to be delivered")
            raise PumpWoodException(
                msg, payload={"mfa_code": "delivery_timeout"})

        if message.status in ['delivered', 'sent']:
            return True

        print_msg = (
            "### Waiting 1 second to check if MFA Twilio SMS was "
            "delivered or queued [{status}]###").format(status=message.status)
        print(print_msg)
        time.sleep(1)
        i = i + 1
