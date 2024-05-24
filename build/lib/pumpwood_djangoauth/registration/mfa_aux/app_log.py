"""Implement MFA for app log."""


def send_code(mfa_method: str, code):
    """
    Send MFA authenticatication code to stdout.

    Args:
        code [str]: MFA code.
        user: Django user to send message to.
    """
    user = mfa_method.user
    stdout_print = (
        "## MFA Authentication Code ## username[{username}] id[{id}] "
        "code[{code}]").format(
            username=user.username, id=user.id, code=code)
    print(stdout_print)
    return True
