from django.contrib import admin
from .models import Locations, Lockers, Reservations


admin.site.register(Reservations)
admin.site.register(Locations)
admin.site.register(Lockers)

