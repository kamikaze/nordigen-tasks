from django.conf import settings
from django.db import models


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    institution_id = models.CharField(max_length=255)
    external_id = models.UUIDField()
    iban = models.CharField(max_length=32)  # Longest known IBAN is 29 character long for Malta
    currency = models.CharField(max_length=3)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'institution_id', 'iban']),
        ]
        unique_together = [['user', 'iban']]


class AccountBalance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    closing_booked = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    expected = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    forward_available = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    interim_available = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    interim_booked = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    non_invoiced = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    opening_booked = models.DecimalField(decimal_places=2, max_digits=10, null=True)


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    institution_id = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    external_id = models.CharField(max_length=255)
    booking_date = models.DateField()
    creditor_account = models.CharField(max_length=32, null=True)
    creditor_name = models.CharField(max_length=255, null=True)
    debtor_account = models.CharField(max_length=32, null=True)
    debtor_name = models.CharField(max_length=255, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    currency = models.CharField(max_length=3)

    iban = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'account_id']),
        ]
        unique_together = [['user', 'account_id', 'external_id']]


class InstitutionAccess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # So what Django gives me to have unlimited VARCHAR?
    agreement_id = models.CharField(max_length=255)
    institution_id = models.CharField(max_length=255)
    reference_id = models.CharField(max_length=255)
    is_granted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'institution_id', 'reference_id']),
        ]
        unique_together = [['agreement_id', 'institution_id']]
        verbose_name_plural = 'Institution accesses'
