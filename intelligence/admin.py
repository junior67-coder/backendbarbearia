from django.contrib import admin

from .models import FrequencySuggestion

# Register your models here.

@admin.register(FrequencySuggestion)
class FrequencySuggestionAdmin(admin.ModelAdmin):
    list_display = ('barbershop', 'service', 'ideal_return_days', 'anticipation_tolerance_days')
    search_fields = ('barbershop__name', 'service__name')
    list_filter = ('barbershop',)
    ordering = ('barbershop', 'service')
