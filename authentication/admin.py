from django.contrib import admin

from .models import BarberShop

# Register your models here.

# admin.site.register(BarberShop)

@admin.register(BarberShop)
class AdminBarberShop(admin.ModelAdmin):
    list_display = ('name', 'cnpj', 'email', 'plans', 'active','date_register',)
    search_fields = ('name', 'plans', 'date_register',)