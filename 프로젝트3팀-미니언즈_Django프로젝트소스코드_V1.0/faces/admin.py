from django.contrib import admin
from .models import Faces

@admin.register(Faces)
class ReservationsAdmin(admin.ModelAdmin):
    list_display = ('user',)



