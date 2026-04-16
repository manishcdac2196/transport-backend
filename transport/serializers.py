from rest_framework import serializers
from django.utils import timezone
from .models import (
    Bus, Trip, Student, MaintenanceLog, FuelLog,
    Payer, Charge, Payment, Driver, SalaryAdvance,
    Loan, LoanRepayment, BusDocument, Route, Stop,
    Cleaner, CleanerAdvance, CleanerLoan, CleanerLoanRepayment,
    ExternalContact, TripLog, Holiday,
)


class BusSerializer(serializers.ModelSerializer):
    profit = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()
    total_expense = serializers.SerializerMethodField()
    days_since_last_maintenance = serializers.SerializerMethodField()
    avg_mileage = serializers.SerializerMethodField()

    class Meta:
        model = Bus
        fields = '__all__'

    def get_profit(self, obj): return obj.get_profit()
    def get_revenue(self, obj): return obj.get_total_revenue()
    def get_total_expense(self, obj): return obj.get_total_expense()
    def get_days_since_last_maintenance(self, obj): return obj.get_days_since_last_maintenance()
    def get_avg_mileage(self, obj): return obj.get_avg_mileage()


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = '__all__'


class StopSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Stop
        fields = '__all__'

    def get_student_count(self, obj):
        return obj.students.count()


class StudentSerializer(serializers.ModelSerializer):
    trip_name = serializers.SerializerMethodField()
    stop_name = serializers.SerializerMethodField()
    source_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = '__all__'

    def get_trip_name(self, obj): return obj.trip.name if obj.trip else None
    def get_stop_name(self, obj): return obj.stop.name if obj.stop else None
    def get_source_name(self, obj): return obj.trip.source_name if obj.trip else None


class MaintenanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceLog
        fields = '__all__'


class FuelLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelLog
        fields = '__all__'


class PayerSerializer(serializers.ModelSerializer):
    total_paid = serializers.SerializerMethodField()
    total_charged = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    total_paid_this_month = serializers.SerializerMethodField()
    total_charged_this_month = serializers.SerializerMethodField()
    balance_this_month = serializers.SerializerMethodField()

    class Meta:
        model = Payer
        fields = '__all__'

    def get_total_paid(self, obj): return obj.total_paid()
    def get_total_charged(self, obj): return obj.total_charged()
    def get_balance(self, obj): return obj.total_charged() - obj.total_paid()
    def get_total_paid_this_month(self, obj): return obj.total_paid_this_month()
    def get_total_charged_this_month(self, obj): return obj.total_charged_this_month()
    def get_balance_this_month(self, obj): return obj.total_charged_this_month() - obj.total_paid_this_month()


class ChargeSerializer(serializers.ModelSerializer):
    payer_name = serializers.SerializerMethodField()
    trip_name = serializers.SerializerMethodField()

    class Meta:
        model = Charge
        fields = '__all__'

    def get_payer_name(self, obj): return obj.payer.name
    def get_trip_name(self, obj): return obj.trip.name


class PaymentSerializer(serializers.ModelSerializer):
    payer_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = '__all__'

    def get_payer_name(self, obj): return obj.payer.name


class SalaryAdvanceSerializer(serializers.ModelSerializer):
    driver_name = serializers.SerializerMethodField()

    class Meta:
        model = SalaryAdvance
        fields = '__all__'

    def get_driver_name(self, obj): return obj.driver.name


class LoanRepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRepayment
        fields = '__all__'


class LoanSerializer(serializers.ModelSerializer):
    amount_repaid = serializers.SerializerMethodField()
    outstanding = serializers.SerializerMethodField()
    driver_name = serializers.SerializerMethodField()
    repayments = LoanRepaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Loan
        fields = '__all__'

    def get_amount_repaid(self, obj): return obj.amount_repaid()
    def get_outstanding(self, obj): return obj.outstanding()
    def get_driver_name(self, obj): return obj.driver.name


class DriverSerializer(serializers.ModelSerializer):
    total_advance_this_month = serializers.SerializerMethodField()
    total_advance_all_time = serializers.SerializerMethodField()
    bus_number = serializers.SerializerMethodField()
    total_loan_outstanding = serializers.SerializerMethodField()

    class Meta:
        model = Driver
        fields = '__all__'

    def get_total_advance_this_month(self, obj):
        now = timezone.now()
        return sum(a.amount for a in obj.advances.filter(
            date__year=now.year, date__month=now.month))

    def get_total_advance_all_time(self, obj):
        return sum(a.amount for a in obj.advances.all())

    def get_bus_number(self, obj):
        return obj.bus.bus_number if obj.bus else None

    def get_total_loan_outstanding(self, obj):
        return sum(loan.outstanding() for loan in obj.loans.all())


class CleanerAdvanceSerializer(serializers.ModelSerializer):
    cleaner_name = serializers.SerializerMethodField()

    class Meta:
        model = CleanerAdvance
        fields = '__all__'

    def get_cleaner_name(self, obj): return obj.cleaner.name


class CleanerLoanRepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CleanerLoanRepayment
        fields = '__all__'


class CleanerLoanSerializer(serializers.ModelSerializer):
    amount_repaid = serializers.SerializerMethodField()
    outstanding = serializers.SerializerMethodField()
    cleaner_name = serializers.SerializerMethodField()
    repayments = CleanerLoanRepaymentSerializer(many=True, read_only=True)

    class Meta:
        model = CleanerLoan
        fields = '__all__'

    def get_amount_repaid(self, obj): return obj.amount_repaid()
    def get_outstanding(self, obj): return obj.outstanding()
    def get_cleaner_name(self, obj): return obj.cleaner.name


class CleanerSerializer(serializers.ModelSerializer):
    total_advance_this_month = serializers.SerializerMethodField()
    bus_number = serializers.SerializerMethodField()
    total_loan_outstanding = serializers.SerializerMethodField()

    class Meta:
        model = Cleaner
        fields = '__all__'

    def get_total_advance_this_month(self, obj):
        now = timezone.now()
        return sum(a.amount for a in obj.advances.filter(
            date__year=now.year, date__month=now.month))

    def get_bus_number(self, obj):
        return obj.bus.bus_number if obj.bus else None

    def get_total_loan_outstanding(self, obj):
        return sum(loan.outstanding() for loan in obj.loans.all())


class ExternalContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalContact
        fields = '__all__'


class TripLogSerializer(serializers.ModelSerializer):
    trip_name = serializers.SerializerMethodField()
    driver_name = serializers.SerializerMethodField()
    cleaner_name = serializers.SerializerMethodField()
    merged_bus_number = serializers.SerializerMethodField()
    source_name = serializers.SerializerMethodField()

    class Meta:
        model = TripLog
        fields = '__all__'

    def get_trip_name(self, obj): return obj.trip.name
    def get_driver_name(self, obj): return obj.driver.name if obj.driver else None
    def get_cleaner_name(self, obj): return obj.cleaner.name if obj.cleaner else None
    def get_merged_bus_number(self, obj): return obj.merged_with_bus.bus_number if obj.merged_with_bus else None
    def get_source_name(self, obj): return obj.trip.source_name


class BusDocumentSerializer(serializers.ModelSerializer):
    days_until_expiry = serializers.SerializerMethodField()
    doc_type_display = serializers.SerializerMethodField()

    class Meta:
        model = BusDocument
        fields = '__all__'

    def get_days_until_expiry(self, obj): return obj.days_until_expiry()
    def get_doc_type_display(self, obj): return obj.get_doc_type_display()


class RouteSerializer(serializers.ModelSerializer):
    stops = StopSerializer(many=True, read_only=True)
    bus_number = serializers.SerializerMethodField()
    trip_name = serializers.SerializerMethodField()

    class Meta:
        model = Route
        fields = '__all__'

    def get_bus_number(self, obj): return obj.bus.bus_number if obj.bus else None
    def get_trip_name(self, obj): return obj.trip.name if obj.trip else None