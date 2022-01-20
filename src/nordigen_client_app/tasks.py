import uuid
from decimal import Decimal

from celery import group
from django.db import transaction

from magic_service_app.celery import app
from nordigen_client_app.models import Account, InstitutionAccess, Transaction, AccountBalance
from nordigen_client_app.nordigen_client import NORDIGEN_CLIENT


@app.task(bind=True)
def enable_institution(self, user_id: int, institution_id: str, reference_id: str):
    access = InstitutionAccess.objects.get(
        user_id=user_id, institution_id=institution_id, reference_id=reference_id
    )
    access.is_granted = True
    access.save(update_fields=('is_granted',))


def fetch_institution_account_ids(user_id: int, institution_id: str):
    requisitions = NORDIGEN_CLIENT.requisition.get_requisitions()
    print(f'{user_id=} {institution_id=}')
    print(requisitions)

    # TODO: filter by requisition ids! for a particular user_id. Use reference_id from InstitutionAccess.

    account_ids = tuple(
        account_id
        for requisition in requisitions['results']
        for account_id in requisition['accounts']
    )

    return account_ids


@app.task(bind=True)
def update_institution(self, user_id: int, institution_id: str):
    external_ids = fetch_institution_account_ids(user_id, institution_id)
    workflow = group(
        (
                fetch_account_details.si(user_id, institution_id, external_id) |
                group(
                    fetch_account_balances.s(),
                    fetch_account_transactions.s()
                )
        ) for external_id in external_ids
    )

    workflow.delay()


@app.task(bind=True)
def fetch_account_details(self, user_id: int, institution_id: str, external_id: str):
    print(f'Request: {self.request!r}')
    print(f'{user_id=} {external_id=}')
    response = NORDIGEN_CLIENT.account_api(external_id).get_details()
    account_details = response['account']

    account, created = Account.objects.update_or_create(
        user_id=user_id,
        external_id=uuid.UUID(external_id),
        institution_id=institution_id,
        iban=account_details['iban'],
        currency=account_details['currency']
    )

    return account.id


@app.task(bind=True)
def fetch_account_balances(self, account_id: int):
    account = Account.objects.get(pk=account_id)
    balances = NORDIGEN_CLIENT.account_api(str(account.external_id)).get_balances()
    balances = {item['balanceType']: Decimal(item['balanceAmount']['amount']) for item in balances['balances']}

    AccountBalance.objects.update_or_create(
        account_id=account_id,
        closing_booked=balances.get('closingBooked'),
        expected=balances.get('expected'),
        forward_available=balances.get('forwardAvailable'),
        interim_available=balances.get('interimAvailable'),
        interim_booked=balances.get('interimBooked'),
        non_invoiced=balances.get('nonInvoiced'),
        opening_booked=balances.get('openingBooked')
    )


@app.task(bind=True)
def fetch_account_transactions(self, account_id: int):
    account = Account.objects.get(pk=account_id)
    user_id = account.user_id
    institution_id = account.institution_id
    transactions = NORDIGEN_CLIENT.account_api(str(account.external_id)).get_transactions()['transactions']

    with transaction.atomic():
        for item in transactions['booked']:
            transaction_amount = item['transactionAmount']
            creditor_account = item.get('creditorAccount')
            debtor_account = item.get('debtorAccount')

            Transaction.objects.update_or_create(
                user_id=user_id,
                institution_id=institution_id,
                account_id=account_id,
                external_id=item['transactionId'],
                booking_date=item['bookingDate'],
                creditor_account=creditor_account['iban'] if creditor_account else None,
                creditor_name=item.get('creditorName'),
                debtor_account=debtor_account['iban'] if debtor_account else None,
                debtor_name=item.get('debtorName'),
                amount=transaction_amount['amount'],
                currency=transaction_amount['currency']
            )
