"""Main method to send MFA codes."""
import os
from pumpwood_djangoauth.registration.mfa_aux import app_log
from pumpwood_djangoauth.registration.mfa_aux import twilio_sms
from pumpwood_communication.exceptions import PumpWoodNotImplementedError


type_function_dict = {
    'app_log': app_log.send_code,
    'sms': twilio_sms.send_code,
}


def send_mfa_code(mfa_method: str, code: str):
    """
    Send mfa code using enviroment variable PUMPWOOD__MFA__APPLICATION_NAME.

    Args:
        type [str]: Type of the MFA backend.
        code [str]: Code to be send for mfa validation.
    """
    fun_send_code = type_function_dict.get(mfa_method.type)
    if fun_send_code is not None:
        fun_send_code(mfa_method=mfa_method, code=code)
    else:
        msg = "[{}] MFA authentication was not implemented".format(
            mfa_method.type)
        raise PumpWoodNotImplementedError(msg, payload={
            'mfa_type': 'not_implemented'})
    return True
