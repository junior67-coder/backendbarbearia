from rest_framework import serializers

from schedulingservices.models import Scheduling, Professional, Service, Client
from authentication.models import BarberShop


class ProfessionalSerializer(serializers.ModelSerializer):
    barber_shop_name = serializers.CharField(source='barbershop.name', read_only=True)
    class Meta:
        model = Professional
        fields = ('id', 'name', 'phone', 'commission_standard', 'ative', 'barber_shop_name')
        

class ServiceSerializer(serializers.ModelSerializer):
    profissionals_aptos = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Professional.objects.all(),
    )
    
    class Meta:
        model = Service
        fields = ('id', 'name', 'minutes_duration', 'value', 'profissionals_aptos')
    