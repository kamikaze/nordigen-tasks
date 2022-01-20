from django.contrib import admin
from nordigen_client_app import models


@admin.register(models.InstitutionAccess)
class InstitutionAccessAdmin(admin.ModelAdmin):
    list_display = ['user', 'agreement_id', 'institution_id', 'reference_id', 'is_granted', 'created_at', 'updated_at']


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'iban', 'created_at', 'updated_at']
