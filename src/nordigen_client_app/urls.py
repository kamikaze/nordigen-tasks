from django.urls import path

from nordigen_client_app.views import (
    account_transactions, connect_institution, new_institution, on_institution_access_granted, user_accounts
)

urlpatterns = [
    path('accounts/', user_accounts, name='user-accounts'),
    path('accounts/<account_id>/transactions/', account_transactions, name='account-transactions'),
    path('institutions/<institution_id>/connect', connect_institution),
    path('institutions/<institution_id>/granted', on_institution_access_granted),
    path('institutions/new', new_institution, name='new-institution'),
]
