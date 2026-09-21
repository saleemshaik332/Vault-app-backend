from django.contrib import admin
from .models import PANCard, DrivingLicense, StudyCertificate, BankDetail

admin.site.register(PANCard)
admin.site.register(DrivingLicense)
admin.site.register(StudyCertificate)
admin.site.register(BankDetail)
