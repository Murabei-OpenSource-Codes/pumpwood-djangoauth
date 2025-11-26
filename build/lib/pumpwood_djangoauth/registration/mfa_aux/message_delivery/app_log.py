"""Implement MFA for app log."""


def send_code(mfa_method: object, code: str) -> bool:
    """Send MFA authenticatication code to stdout.

    This may be used for testing process.

    Args:
        code (str):
            MFA code.
        mfa_method (object):
            MFA method that is logged.

    Results:
        Return True.
    """
    user = mfa_method.user
    msg_template = (
        "## MFA Authentication Code ## username[{username}] id[{id}] "
        "code[{code}]")
    stdout_print = msg_template.format(
        username=user.username, id=user.id, code=code)
    print(stdout_print)
    return True
