from django.contrib import admin
from .models import Professional, Service, Client, Scheduling

# Register your models here.


@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('name', 'barbershop', 'commission_standard', 'ative')
    list_filter = ('barbershop', 'commission_standard', 'ative')
    search_fields = ('name', 'barbershop', 'commission_standard', 'ative')
    list_per_page = 10
    

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'barbershop', 'minutes_duration', 'value')
    list_filter = ('barbershop', 'minutes_duration', 'value')
    search_fields = ('name', 'barbershop', 'minutes_duration', 'value')
    list_per_page = 10
    
    
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'barbershop', 'phone_whatsap', 'email')
    list_filter = ('barbershop', 'phone_whatsap', 'email')
    search_fields = ('name', 'barbershop', 'phone_whatsap', 'email')
    list_per_page = 10
    
    
@admin.register(Scheduling)
class SchedulingAdmin(admin.ModelAdmin):
    list_display = ('client', 'professional', 'service', 'date_hour_init', 'date_hour_end', 'initial_value')
    list_filter = ('client', 'professional', 'service', 'date_hour_init', 'date_hour_end', 'initial_value')
    search_fields = ('client', 'professional', 'service', 'date_hour_init', 'date_hour_end', 'initial_value')
    list_per_page = 10
