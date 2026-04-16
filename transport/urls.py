from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    BusViewSet, TripViewSet, StudentViewSet,
    MaintenanceLogViewSet, FuelLogViewSet,
    PayerViewSet, ChargeViewSet, PaymentViewSet,
    DriverViewSet, SalaryAdvanceViewSet,
    LoanViewSet, LoanRepaymentViewSet,
    BusDocumentViewSet, RouteViewSet, StopViewSet,
    CleanerViewSet, CleanerAdvanceViewSet,
    CleanerLoanViewSet, CleanerLoanRepaymentViewSet,
    ExternalContactViewSet, TripLogViewSet,
    HolidayViewSet, login_view, trips_today,
)

router = DefaultRouter()
router.register(r'buses', BusViewSet)
router.register(r'trips', TripViewSet)
router.register(r'students', StudentViewSet)
router.register(r'maintenance', MaintenanceLogViewSet)
router.register(r'fuel', FuelLogViewSet)
router.register(r'payers', PayerViewSet)
router.register(r'charges', ChargeViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'drivers', DriverViewSet)
router.register(r'salary-advances', SalaryAdvanceViewSet)
router.register(r'loans', LoanViewSet, basename='loan')
router.register(r'loan-repayments', LoanRepaymentViewSet)
router.register(r'bus-documents', BusDocumentViewSet, basename='busdocument')
router.register(r'routes', RouteViewSet)
router.register(r'stops', StopViewSet)
router.register(r'cleaners', CleanerViewSet)
router.register(r'cleaner-advances', CleanerAdvanceViewSet)
router.register(r'cleaner-loans', CleanerLoanViewSet, basename='cleanerloan')
router.register(r'cleaner-loan-repayments', CleanerLoanRepaymentViewSet)
router.register(r'external-contacts', ExternalContactViewSet)
router.register(r'trip-logs', TripLogViewSet)
router.register(r'holidays', HolidayViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', login_view),
    path('trips-today/', trips_today),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)