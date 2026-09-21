from rest_framework.routers import DefaultRouter
from .views import PANCardViewSet, DrivingLicenseViewSet, StudyCertificateViewSet, BankDetailViewSet

router = DefaultRouter()
router.register('pan-cards', PANCardViewSet, basename='pancard')
router.register('driving-licenses', DrivingLicenseViewSet, basename='drivinglicense')
router.register('study-certificates', StudyCertificateViewSet, basename='studycertificate')
router.register('bank-details', BankDetailViewSet, basename='bankdetail')

urlpatterns = router.urls
