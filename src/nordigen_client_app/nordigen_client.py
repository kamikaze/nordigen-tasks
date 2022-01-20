from django.conf import settings
from nordigen import NordigenClient


NORDIGEN_CLIENT = NordigenClient(
    secret_id=settings.NORDIGEN_ID,
    secret_key=settings.NORDIGEN_KEY
)
NORDIGEN_CLIENT.generate_token()
