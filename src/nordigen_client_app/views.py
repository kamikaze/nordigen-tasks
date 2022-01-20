from uuid import uuid4

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy

from nordigen_client_app.models import InstitutionAccess, Account, Transaction, AccountBalance
from nordigen_client_app.nordigen_client import NORDIGEN_CLIENT
from nordigen_client_app.tasks import enable_institution, update_institution


@login_required
def user_accounts(request):
    accounts = Account.objects.filter(user=request.user)
    account_balances = AccountBalance.objects.filter(user=request.user)
    account_balances = {item.id: item.interim_available for item in account_balances}
    accounts = {
       account.id: {
           'iban': account.iban,
           'currency': account.currency,
           'balance': account_balances.get(account.id),
       }
       for account in accounts
    }

    return render(request, 'user_accounts.html', {'accounts': accounts})


@login_required
def account_transactions(request, account_id: str):
    transactions = Transaction.objects.filter(user=request.user, account_id=account_id)

    return render(request, 'account_transactions.html', {'transactions': transactions})


@login_required
def new_institution(request):
    institutions = NORDIGEN_CLIENT.institution.get_institutions('LV')

    return render(request, 'new_institution.html', {'institutions': institutions})


@login_required
def connect_institution(request, institution_id: str):
    agreement = NORDIGEN_CLIENT.agreement.create_agreement(institution_id)
    reference_id = str(uuid4())

    InstitutionAccess.objects.create(
        user=request.user,
        agreement_id=agreement['id'],
        institution_id=institution_id,
        reference_id=reference_id,
        is_granted=False
    )

    redirect_uri = f'{settings.SERVICE_ADDRESS}/magic/institutions/{institution_id}/granted'
    requisition = NORDIGEN_CLIENT.requisition.create_requisition(redirect_uri, reference_id, institution_id,
                                                                 agreement['id'])
    print(requisition)
    return HttpResponseRedirect(requisition['link'])


@login_required
def on_institution_access_granted(request, institution_id: str):
    print(request)
    user = request.user
    reference_id = request.GET['ref']
    user_id = user.id
    job_canvas = (
        enable_institution.si(user_id, institution_id, reference_id) |
        update_institution.si(user_id, institution_id)
    )
    result = job_canvas()
    print(result.get())

    return HttpResponseRedirect(reverse_lazy('user-accounts'))


def index(request):
    return HttpResponseRedirect(reverse_lazy('user-accounts'))
