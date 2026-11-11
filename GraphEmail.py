"""Send mail through Graph using CLIENT_SECRET from a local secret_key.py file."""
from servicenow_alert import install_exception_hooks as _install_servicenow_exception_hooks
_install_servicenow_exception_hooks()


import base64
from email.policy import SMTP
from email.utils import getaddresses

import requests

try:
    from secret_key import CLIENT_SECRET
except ModuleNotFoundError as error:
    if error.name != "secret_key":
        raise
    raise RuntimeError(
        "Graph client secret is missing. Create secret_key.py beside GraphEmail.py "
        "and define CLIENT_SECRET = 'your-rotated-secret'."
    ) from error


FROM_ADDRESS = "ExecutiveMorningReport@csx.com"
CLIENT_ID = "30ed551c-733e-4889-8067-a5ebe1f69f22"
TENANT_ID = "432c14c7-79c4-4679-bcc6-448d1efefb0f"
GRAPH_SCOPE = "https://graph.microsoft.com/.default"


def get_access_token():
    if not CLIENT_SECRET:
        raise RuntimeError("CLIENT_SECRET in secret_key.py is empty.")
    response = requests.post(
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
        data={
            "client_id": CLIENT_ID,
            "scope": GRAPH_SCOPE,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
        },
        timeout=30,
    )
    response.raise_for_status()
    access_token = response.json().get("access_token")
    if not access_token:
        raise RuntimeError("Microsoft identity response did not contain an access token.")
    return access_token


def send_graph_email(message, recipients):
    if not recipients:
        raise ValueError("At least one email recipient is required.")

    if "From" in message:
        message.replace_header("From", FROM_ADDRESS)
    else:
        message["From"] = FROM_ADDRESS

    visible_recipients = {
        address.lower()
        for header in ("To", "Cc")
        for _, address in getaddresses(message.get_all(header, []))
    }
    bcc_recipients = [
        address for address in recipients if address.lower() not in visible_recipients
    ]
    if "Bcc" in message:
        del message["Bcc"]
    if bcc_recipients:
        message["Bcc"] = ", ".join(bcc_recipients)

    mime_content = base64.b64encode(message.as_bytes(policy=SMTP)).decode("ascii")
    response = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{FROM_ADDRESS}/sendMail",
        headers={
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "text/plain",
        },
        data=mime_content,
        timeout=60,
    )
    if response.status_code != 202:
        response.raise_for_status()
        raise RuntimeError(
            f"Microsoft Graph returned unexpected status {response.status_code} "
            "while sending email."
        )
