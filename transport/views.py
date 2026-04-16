from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import authenticate
from django.conf import settings
import jwt
import datetime

from .models import (
    Bus, Trip, Student, MaintenanceLog, FuelLog,
    Payer, Charge, Payment, Driver, SalaryAdvance,
    Loan, LoanRepayment, BusDocument, Route, Stop,
    Cleaner, CleanerAdvance, CleanerLoan, CleanerLoanRepayment,
    ExternalContact, TripLog, Holiday,
)
from .serializers import (
    BusSerializer, TripSerializer, StudentSerializer,
    MaintenanceLogSerializer, FuelLogSerializer,
    PayerSerializer, ChargeSerializer, PaymentSerializer,
    DriverSerializer, SalaryAdvanceSerializer,
    LoanSerializer, LoanRepaymentSerializer,
    BusDocumentSerializer, RouteSerializer, StopSerializer,
    CleanerSerializer, CleanerAdvanceSerializer,
    CleanerLoanSerializer, CleanerLoanRepaymentSerializer,
    ExternalContactSerializer, TripLogSerializer, HolidaySerializer,
)


@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user and user.is_staff:
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, settings.SECRET_KEY, algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        return Response({'token': token, 'username': user.username})
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def trips_today(request):
    from django.utils import timezone
    today = timezone.now().date()
    day_abbr = today.strftime('%a').lower()
    all_trips = Trip.objects.all()
    todays_trips = [t for t in all_trips if day_abbr in (t.days_of_week or [])]
    serializer = TripSerializer(todays_trips, many=True)
    existing_logs = TripLog.objects.filter(date=today)
    log_map = {log.trip_id: TripLogSerializer(log).data for log in existing_logs}
    holidays = Holiday.objects.filter(date=today)
    return Response({
        'date': str(today),
        'day': day_abbr,
        'trips': serializer.data,
        'logs': log_map,
        'holidays': [h.name for h in holidays],
    })


class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer


class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all().order_by('date')
    serializer_class = HolidaySerializer


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        bus = self.request.query_params.get('bus')
        if bus:
            qs = qs.filter(bus=bus)
        return qs


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        trip = self.request.query_params.get('trip')
        stop = self.request.query_params.get('stop')
        search = self.request.query_params.get('search')
        source = self.request.query_params.get('source')
        if trip:
            qs = qs.filter(trip=trip)
        if stop:
            qs = qs.filter(stop=stop)
        if search:
            qs = qs.filter(name__icontains=search)
        if source:
            qs = qs.filter(trip__source_name__icontains=source)
        return qs


class MaintenanceLogViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceLog.objects.all()
    serializer_class = MaintenanceLogSerializer

    def get_queryset(self):
        qs = super().get_queryset().order_by('-date')
        bus = self.request.query_params.get('bus')
        if bus:
            qs = qs.filter(bus=bus)
        return qs


class FuelLogViewSet(viewsets.ModelViewSet):
    queryset = FuelLog.objects.all()
    serializer_class = FuelLogSerializer

    def get_queryset(self):
        qs = super().get_queryset().order_by('-date')
        bus = self.request.query_params.get('bus')
        if bus:
            qs = qs.filter(bus=bus)
        return qs


class PayerViewSet(viewsets.ModelViewSet):
    queryset = Payer.objects.all()
    serializer_class = PayerSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        payer_type = self.request.query_params.get('type')
        if search:
            qs = qs.filter(name__icontains=search)
        if payer_type:
            qs = qs.filter(payer_type=payer_type)
        return qs


class ChargeViewSet(viewsets.ModelViewSet):
    queryset = Charge.objects.all()
    serializer_class = ChargeSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        payer = self.request.query_params.get('payer')
        if payer:
            qs = qs.filter(payer=payer)
        return qs


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        payer = self.request.query_params.get('payer')
        if payer:
            qs = qs.filter(payer=payer)
        return qs


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs


class SalaryAdvanceViewSet(viewsets.ModelViewSet):
    queryset = SalaryAdvance.objects.all()
    serializer_class = SalaryAdvanceSerializer

    def get_queryset(self):
        qs = super().get_queryset().order_by('-date')
        driver = self.request.query_params.get('driver')
        if driver:
            qs = qs.filter(driver=driver)
        return qs


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        driver = self.request.query_params.get('driver')
        if driver:
            qs = qs.filter(driver=driver)
        return qs


class LoanRepaymentViewSet(viewsets.ModelViewSet):
    queryset = LoanRepayment.objects.all()
    serializer_class = LoanRepaymentSerializer


class CleanerViewSet(viewsets.ModelViewSet):
    queryset = Cleaner.objects.all()
    serializer_class = CleanerSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs


class CleanerAdvanceViewSet(viewsets.ModelViewSet):
    queryset = CleanerAdvance.objects.all()
    serializer_class = CleanerAdvanceSerializer

    def get_queryset(self):
        qs = super().get_queryset().order_by('-date')
        cleaner = self.request.query_params.get('cleaner')
        if cleaner:
            qs = qs.filter(cleaner=cleaner)
        return qs


class CleanerLoanViewSet(viewsets.ModelViewSet):
    queryset = CleanerLoan.objects.all()
    serializer_class = CleanerLoanSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        cleaner = self.request.query_params.get('cleaner')
        if cleaner:
            qs = qs.filter(cleaner=cleaner)
        return qs


class CleanerLoanRepaymentViewSet(viewsets.ModelViewSet):
    queryset = CleanerLoanRepayment.objects.all()
    serializer_class = CleanerLoanRepaymentSerializer


class ExternalContactViewSet(viewsets.ModelViewSet):
    queryset = ExternalContact.objects.all()
    serializer_class = ExternalContactSerializer


class TripLogViewSet(viewsets.ModelViewSet):
    queryset = TripLog.objects.all()
    serializer_class = TripLogSerializer

    def get_queryset(self):
        qs = super().get_queryset().order_by('-date')
        date = self.request.query_params.get('date')
        trip = self.request.query_params.get('trip')
        if date:
            qs = qs.filter(date=date)
        if trip:
            qs = qs.filter(trip=trip)
        return qs


class BusDocumentViewSet(viewsets.ModelViewSet):
    queryset = BusDocument.objects.all()
    serializer_class = BusDocumentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = super().get_queryset().order_by('expiry_date')
        bus = self.request.query_params.get('bus')
        if bus:
            qs = qs.filter(bus=bus)
        return qs


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class StopViewSet(viewsets.ModelViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        route = self.request.query_params.get('route')
        if route:
            qs = qs.filter(route=route)
        return qs