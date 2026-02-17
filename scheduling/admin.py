from django.contrib import admin
from .models import BarberShop, Service, Client, Appointment

# Register your models here.

@admin.register(BarberShop)
class BarberShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'subscription_plan', 'created_at')
    search_fields = ('name', 'owner__username')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_minutes', 'barbershop')
    list_filter = ('barbershop',)
    search_fields = ('name',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'nickname', 'barbershop')
    list_filter = ('barbershop',)
    search_fields = ('name', 'phone')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'service', 'date', 'time', 'status', 'barbershop')
    list_filter = ('status', 'date', 'barbershop')
    search_fields = ('client__name', 'service__name')
    ordering = ('-date', '-time')

