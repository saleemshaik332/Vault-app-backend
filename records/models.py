from django.conf import settings
from django.db import models
from django.utils import timezone

from vaultproject.crypto_utils import encrypt_value, decrypt_value, mask_value


class SoftDeleteMixin(models.Model):
    """Adds Trash/Restore/Permanent-delete behaviour to any record model."""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class PANCard(SoftDeleteMixin):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pan_cards')
    full_name = models.CharField(max_length=150)
    pan_number_encrypted = models.TextField()
    date_of_birth = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    @property
    def pan_number(self):
        return decrypt_value(self.pan_number_encrypted)

    @pan_number.setter
    def pan_number(self, value):
        self.pan_number_encrypted = encrypt_value(value)

    @property
    def pan_number_masked(self):
        return mask_value(self.pan_number)

    def __str__(self):
        return f"PAN - {self.full_name}"


class DrivingLicense(SoftDeleteMixin):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='driving_licenses')
    full_name = models.CharField(max_length=150)
    dl_number_encrypted = models.TextField()
    issuing_state = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    vehicle_classes = models.CharField(max_length=150, blank=True, help_text="e.g. LMV, MCWG")
    notes = models.TextField(blank=True)

    @property
    def dl_number(self):
        return decrypt_value(self.dl_number_encrypted)

    @dl_number.setter
    def dl_number(self, value):
        self.dl_number_encrypted = encrypt_value(value)

    @property
    def dl_number_masked(self):
        return mask_value(self.dl_number)

    def __str__(self):
        return f"DL - {self.full_name}"


class StudyCertificate(SoftDeleteMixin):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_certificates')
    title = models.CharField(max_length=200, help_text="e.g. B.Tech Computer Science")
    institution = models.CharField(max_length=200)
    certificate_number_encrypted = models.TextField(blank=True)
    year_of_completion = models.PositiveIntegerField(null=True, blank=True)
    grade_or_percentage = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    @property
    def certificate_number(self):
        return decrypt_value(self.certificate_number_encrypted)

    @certificate_number.setter
    def certificate_number(self, value):
        self.certificate_number_encrypted = encrypt_value(value)

    def __str__(self):
        return f"Certificate - {self.title}"


class BankDetail(SoftDeleteMixin):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bank_details')
    bank_name = models.CharField(max_length=150)
    account_holder_name = models.CharField(max_length=150)
    account_number_encrypted = models.TextField()
    ifsc_or_swift_code = models.CharField(max_length=30, blank=True)
    branch = models.CharField(max_length=150, blank=True)
    account_type = models.CharField(max_length=50, blank=True, help_text="e.g. Savings, Current")
    notes = models.TextField(blank=True)

    @property
    def account_number(self):
        return decrypt_value(self.account_number_encrypted)

    @account_number.setter
    def account_number(self, value):
        self.account_number_encrypted = encrypt_value(value)

    @property
    def account_number_masked(self):
        return mask_value(self.account_number)

    def __str__(self):
        return f"Bank - {self.bank_name} ({self.account_holder_name})"
