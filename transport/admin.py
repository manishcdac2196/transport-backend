from django.contrib import admin
from .models import Student, Bus, Trip
from .models import MaintenanceLog
from .models import FuelLog
from .models import Payer, Charge, Payment
from .models import Driver
from .models import SalaryAdvance

class TripInline(admin.TabularInline):
    model = Trip
    extra = 0

class MaintenanceInline(admin.TabularInline):
    model = MaintenanceLog
    extra = 0

class FuelInline(admin.TabularInline):
    model = FuelLog
    extra = 0


class BusAdmin(admin.ModelAdmin):
    inlines = [TripInline, MaintenanceInline, FuelInline]


admin.site.register(Student)
admin.site.register(Bus, BusAdmin)
admin.site.register(Trip)
admin.site.register(MaintenanceLog)
admin.site.register(Payer)
admin.site.register(Charge)
admin.site.register(Payment)
admin.site.register(Driver)
admin.site.register(SalaryAdvance)

class FuelLogAdmin(admin.ModelAdmin):
    list_display = ('bus', 'date', 'liters', 'cost', 'odometer_reading', 'mileage_display')
    list_filter = ('bus', 'date')
    search_fields = ('bus__bus_number',)

    def mileage_display(self, obj):
        mileage = obj.get_mileage()
        return round(mileage, 2) if mileage else "-"
    
    mileage_display.short_description = "Mileage (km/l)"


admin.site.register(FuelLog, FuelLogAdmin)