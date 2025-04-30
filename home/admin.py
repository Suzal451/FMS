from django.contrib import admin

# Register your models here.
from home.models import Register
from home.models import Getdatetime
from home.models import Bookings
from home.models import Payment

admin.site.register(Getdatetime)
admin.site.register(Register)
admin.site.register(Bookings)
admin.site.register(Payment)
