from django.db import models
from django.utils import timezone

DAYS_OF_WEEK = [
    ('mon', 'Monday'),
    ('tue', 'Tuesday'),
    ('wed', 'Wednesday'),
    ('thu', 'Thursday'),
    ('fri', 'Friday'),
    ('sat', 'Saturday'),
    ('sun', 'Sunday'),
]

class Bus(models.Model):
    bus_number = models.CharField(max_length=20, unique=True)
    capacity = models.IntegerField()

    def __str__(self):
        return self.bus_number

    class Meta:
        verbose_name = "Bus"
        verbose_name_plural = "Buses"

    def get_total_revenue(self):
        from django.utils import timezone
        now = timezone.now()
        total = 0
        for trip in self.trips.all():
            for charge in trip.charges.all():
                if charge.frequency == 'monthly':
                    total += charge.amount
                elif charge.frequency == 'quarterly':
                    total += charge.amount / 3
                elif charge.frequency == 'yearly':
                    total += charge.amount / 12
        return round(total, 2)

    def get_total_expense(self):
        fuel_cost = sum(f.cost for f in self.fuel_logs.all())
        maintenance_cost = sum(m.cost for m in self.maintenance_logs.all())
        return fuel_cost + maintenance_cost

    def get_profit(self):
        return self.get_total_revenue() - self.get_total_expense()

    def get_days_since_last_maintenance(self):
        last = self.maintenance_logs.order_by('-date').first()
        if last:
            return (timezone.now().date() - last.date).days
        return None

    def get_avg_mileage(self):
        logs = list(self.fuel_logs.order_by('odometer_reading'))
        mileages = []
        for i in range(1, len(logs)):
            dist = logs[i].odometer_reading - logs[i-1].odometer_reading
            if logs[i].liters > 0:
                mileages.append(round(dist / logs[i].liters, 2))
        if mileages:
            return round(sum(mileages) / len(mileages), 2)
        return None

class Holiday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=100)
    applies_to = models.CharField(max_length=100, blank=True, null=True,
        help_text="Leave blank for all, or enter school/company name")

    def __str__(self):
        return f"{self.name} — {self.date}"

class Trip(models.Model):
    TRIP_TYPE_CHOICES = [('pickup', 'Pickup'), ('drop', 'Drop')]
    TRIP_SOURCE_CHOICES = [('school', 'School'), ('company', 'Company')]
    source_type = models.CharField(max_length=20, choices=TRIP_SOURCE_CHOICES, default='school')
    source_name = models.CharField(max_length=100)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='trips')
    name = models.CharField(max_length=100)
    trip_type = models.CharField(max_length=10, choices=TRIP_TYPE_CHOICES)
    start_time = models.TimeField()
    estimated_duration = models.IntegerField(help_text="Duration in minutes")
    distance_km = models.FloatField()
    days_of_week = models.JSONField(default=list,
        help_text="List of days this trip runs e.g. ['mon','tue','wed','thu','fri']")

    def __str__(self):
        return f"{self.name} ({self.trip_type})"

    def runs_on(self, date):
        day = date.strftime('%a').lower()
        return day in (self.days_of_week or [])

class Stop(models.Model):
    route = models.ForeignKey('Route', on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    sequence = models.IntegerField()
    estimated_time = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ['sequence']

    def __str__(self):
        return f"{self.route.name} - Stop {self.sequence}: {self.name}"

class Student(models.Model):
    name = models.CharField(max_length=100)
    enrollment_code = models.CharField(max_length=50, unique=True)
    class_name = models.CharField(max_length=20)
    section = models.CharField(max_length=10)
    father_phone = models.CharField(max_length=15)
    mother_phone = models.CharField(max_length=15, blank=True, null=True)
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    stop = models.ForeignKey(Stop, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    def __str__(self):
        return self.name

class MaintenanceLog(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='maintenance_logs')
    date = models.DateField()
    cost = models.FloatField()
    description = models.TextField()
    vendor = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.bus.bus_number} - {self.date}"

class FuelLog(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='fuel_logs')
    date = models.DateField()
    liters = models.FloatField()
    cost = models.FloatField()
    odometer_reading = models.FloatField()

    def __str__(self):
        return f"{self.bus.bus_number} - {self.date}"

    def get_mileage(self):
        previous = FuelLog.objects.filter(
            bus=self.bus, odometer_reading__lt=self.odometer_reading
        ).order_by('-odometer_reading').first()
        if previous:
            distance = self.odometer_reading - previous.odometer_reading
            if self.liters > 0:
                return round(distance / self.liters, 2)

class Payer(models.Model):
    PAYER_TYPE_CHOICES = [('school', 'School'), ('student', 'Student'), ('company', 'Company')]
    name = models.CharField(max_length=100)
    payer_type = models.CharField(max_length=20, choices=PAYER_TYPE_CHOICES)
    contact = models.CharField(max_length=15, blank=True, null=True)

    def total_paid(self):
        return sum(p.amount for p in self.payments.all())

    def total_charged(self):
        return sum(c.amount for c in self.charges.all())

    def total_paid_this_month(self):
        now = timezone.now()
        return sum(p.amount for p in self.payments.filter(
            date__year=now.year, date__month=now.month))

    def total_charged_this_month(self):
        total = 0
        for c in self.charges.all():
            if c.frequency == 'monthly':
                total += c.amount
            elif c.frequency == 'quarterly':
                total += c.amount / 3
            elif c.frequency == 'yearly':
                total += c.amount / 12
        return round(total, 2)

    def __str__(self):
        return f"{self.name} ({self.payer_type})"

class Charge(models.Model):
    FREQUENCY_CHOICES = [('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')]
    payer = models.ForeignKey(Payer, on_delete=models.CASCADE, related_name='charges')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='charges')
    amount = models.FloatField()
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    start_date = models.DateField()

    def __str__(self):
        return f"{self.payer.name} - {self.amount}"

class Payment(models.Model):
    payer = models.ForeignKey(Payer, on_delete=models.CASCADE, related_name='payments')
    amount = models.FloatField()
    date = models.DateField()
    description = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.payer.name} - {self.amount}"

class Driver(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    license_number = models.CharField(max_length=50)
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True, related_name='drivers')
    is_part_time = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    monthly_salary = models.FloatField(default=0)
    photo = models.ImageField(upload_to='driver_photos/', blank=True, null=True)
    license_image = models.ImageField(upload_to='driver_licenses/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name

class SalaryAdvance(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='advances')
    date = models.DateField()
    amount = models.FloatField()
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.driver.name} - {self.amount} on {self.date}"

class Loan(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='loans')
    date_given = models.DateField()
    total_amount = models.FloatField()
    monthly_repayment = models.FloatField(default=0)
    notes = models.TextField(blank=True, null=True)

    def amount_repaid(self):
        return sum(r.amount for r in self.repayments.all())

    def outstanding(self):
        return self.total_amount - self.amount_repaid()

    def __str__(self):
        return f"{self.driver.name} - loan ₹{self.total_amount}"

class LoanRepayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayments')
    date = models.DateField()
    amount = models.FloatField()

    def __str__(self):
        return f"Repayment ₹{self.amount} on {self.date}"

class Cleaner(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True, related_name='cleaners')
    is_active = models.BooleanField(default=True)
    monthly_salary = models.FloatField(default=0)
    photo = models.ImageField(upload_to='cleaner_photos/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name

class CleanerAdvance(models.Model):
    cleaner = models.ForeignKey(Cleaner, on_delete=models.CASCADE, related_name='advances')
    date = models.DateField()
    amount = models.FloatField()
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.cleaner.name} - {self.amount} on {self.date}"

class CleanerLoan(models.Model):
    cleaner = models.ForeignKey(Cleaner, on_delete=models.CASCADE, related_name='loans')
    date_given = models.DateField()
    total_amount = models.FloatField()
    notes = models.TextField(blank=True, null=True)

    def amount_repaid(self):
        return sum(r.amount for r in self.repayments.all())

    def outstanding(self):
        return self.total_amount - self.amount_repaid()

    def __str__(self):
        return f"{self.cleaner.name} - loan ₹{self.total_amount}"

class CleanerLoanRepayment(models.Model):
    loan = models.ForeignKey(CleanerLoan, on_delete=models.CASCADE, related_name='repayments')
    date = models.DateField()
    amount = models.FloatField()

    def __str__(self):
        return f"Repayment ₹{self.amount} on {self.date}"

class ExternalContact(models.Model):
    ROLE_CHOICES = [
        ('driver', 'Driver'), ('cleaner', 'Cleaner'),
        ('mechanic', 'Mechanic'), ('other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='driver')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.role})"

class TripLog(models.Model):
    STATUS_CHOICES = [
        ('normal', 'Normal'),
        ('delayed', 'Delayed'),
        ('cancelled', 'Cancelled'),
        ('merged', 'Merged with another bus'),
        ('driver_changed', 'Driver changed'),
        ('holiday', 'Holiday'),
        ('other', 'Other issue'),
    ]
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='trip_logs')
    cleaner = models.ForeignKey(Cleaner, on_delete=models.SET_NULL, null=True, blank=True, related_name='trip_logs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='normal')
    merged_with_bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True, related_name='merged_logs')
    notes = models.TextField(blank=True, null=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trip', 'date')

    def __str__(self):
        return f"{self.trip.name} - {self.date} - {self.status}"

class BusDocument(models.Model):
    DOC_TYPE_CHOICES = [
        ('rc', 'Registration Certificate'),
        ('permit', 'Contract Carriage Permit'),
        ('fitness', 'Fitness Certificate'),
        ('insurance', 'Insurance'),
        ('puc', 'PUC Certificate'),
        ('other', 'Other'),
    ]
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES)
    expiry_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    document_image = models.ImageField(upload_to='bus_documents/', blank=True, null=True)

    def days_until_expiry(self):
        return (self.expiry_date - timezone.now().date()).days

    def __str__(self):
        return f"{self.bus.bus_number} - {self.doc_type}"

class Route(models.Model):
    name = models.CharField(max_length=100)
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True, related_name='routes')
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True, blank=True, related_name='routes')

    def __str__(self):
        return self.name