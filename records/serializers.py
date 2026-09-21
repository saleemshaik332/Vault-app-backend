from rest_framework import serializers
from .models import PANCard, DrivingLicense, StudyCertificate, BankDetail


class PANCardSerializer(serializers.ModelSerializer):
    pan_number = serializers.CharField(write_only=True)
    pan_number_masked = serializers.ReadOnlyField()

    class Meta:
        model = PANCard
        fields = ['id', 'full_name', 'pan_number', 'pan_number_masked', 'date_of_birth',
                  'notes', 'is_deleted', 'deleted_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_deleted', 'deleted_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        pan_number = validated_data.pop('pan_number')
        instance = PANCard(owner=self.context['request'].user, **validated_data)
        instance.pan_number = pan_number
        instance.save()
        return instance

    def update(self, instance, validated_data):
        pan_number = validated_data.pop('pan_number', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if pan_number:
            instance.pan_number = pan_number
        instance.save()
        return instance


class DrivingLicenseSerializer(serializers.ModelSerializer):
    dl_number = serializers.CharField(write_only=True)
    dl_number_masked = serializers.ReadOnlyField()

    class Meta:
        model = DrivingLicense
        fields = ['id', 'full_name', 'dl_number', 'dl_number_masked', 'issuing_state',
                  'issue_date', 'expiry_date', 'vehicle_classes', 'notes',
                  'is_deleted', 'deleted_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_deleted', 'deleted_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        dl_number = validated_data.pop('dl_number')
        instance = DrivingLicense(owner=self.context['request'].user, **validated_data)
        instance.dl_number = dl_number
        instance.save()
        return instance

    def update(self, instance, validated_data):
        dl_number = validated_data.pop('dl_number', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if dl_number:
            instance.dl_number = dl_number
        instance.save()
        return instance


class StudyCertificateSerializer(serializers.ModelSerializer):
    certificate_number = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = StudyCertificate
        fields = ['id', 'title', 'institution', 'certificate_number', 'year_of_completion',
                  'grade_or_percentage', 'notes', 'is_deleted', 'deleted_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_deleted', 'deleted_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        certificate_number = validated_data.pop('certificate_number', '')
        instance = StudyCertificate(owner=self.context['request'].user, **validated_data)
        instance.certificate_number = certificate_number
        instance.save()
        return instance

    def update(self, instance, validated_data):
        certificate_number = validated_data.pop('certificate_number', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if certificate_number is not None:
            instance.certificate_number = certificate_number
        instance.save()
        return instance


class BankDetailSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(write_only=True)
    account_number_masked = serializers.ReadOnlyField()

    class Meta:
        model = BankDetail
        fields = ['id', 'bank_name', 'account_holder_name', 'account_number', 'account_number_masked',
                  'ifsc_or_swift_code', 'branch', 'account_type', 'notes',
                  'is_deleted', 'deleted_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_deleted', 'deleted_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        account_number = validated_data.pop('account_number')
        instance = BankDetail(owner=self.context['request'].user, **validated_data)
        instance.account_number = account_number
        instance.save()
        return instance

    def update(self, instance, validated_data):
        account_number = validated_data.pop('account_number', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if account_number:
            instance.account_number = account_number
        instance.save()
        return instance
