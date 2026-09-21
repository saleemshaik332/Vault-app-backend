from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import PANCard, DrivingLicense, StudyCertificate, BankDetail
from .serializers import (
    PANCardSerializer, DrivingLicenseSerializer,
    StudyCertificateSerializer, BankDetailSerializer
)


class OwnedSoftDeleteViewSet(viewsets.ModelViewSet):
    """
    Base viewset: scopes every query to the logged-in user's own records,
    and implements soft-delete / trash / restore / permanent-delete.

    - DELETE /<id>/          -> soft delete (moves to trash)
    - GET    /trash/          -> list this user's trashed records
    - POST   /<id>/restore/   -> restore from trash
    - DELETE /<id>/permanent/ -> permanently remove
    """

    def get_queryset(self):
        base_qs = self.queryset.model.objects.filter(owner=self.request.user)
        if self.action == 'trash':
            return base_qs.filter(is_deleted=True)
        return base_qs.filter(is_deleted=False)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response({'message': 'Moved to trash.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def trash(self, request):
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(page or self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        instance = self.queryset.model.objects.filter(owner=request.user, pk=pk, is_deleted=True).first()
        if not instance:
            return Response({'error': 'Not found in trash.'}, status=status.HTTP_404_NOT_FOUND)
        instance.restore()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'], url_path='permanent')
    def permanent_delete(self, request, pk=None):
        instance = self.queryset.model.objects.filter(owner=request.user, pk=pk).first()
        if not instance:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response({'message': 'Permanently deleted.'}, status=status.HTTP_204_NO_CONTENT)


class PANCardViewSet(OwnedSoftDeleteViewSet):
    queryset = PANCard.objects.all()
    serializer_class = PANCardSerializer


class DrivingLicenseViewSet(OwnedSoftDeleteViewSet):
    queryset = DrivingLicense.objects.all()
    serializer_class = DrivingLicenseSerializer


class StudyCertificateViewSet(OwnedSoftDeleteViewSet):
    queryset = StudyCertificate.objects.all()
    serializer_class = StudyCertificateSerializer


class BankDetailViewSet(OwnedSoftDeleteViewSet):
    queryset = BankDetail.objects.all()
    serializer_class = BankDetailSerializer
