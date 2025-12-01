from rest_framework import serializers

from datetime import timedelta

from schedulingservices.models import Scheduling, Professional, Service, Client
from authentication.models import BarberShop


class ProfessionalSerializer(serializers.ModelSerializer):
    barber_shop_name = serializers.CharField(source='barbershop.name', read_only=True)
    class Meta:
        model = Professional
        fields = ('id', 'name', 'phone', 'commission_standard', 'ative', 'barber_shop_name')
        

class ServiceSerializer(serializers.ModelSerializer):
    professionals_aptos = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Professional.objects.all(),
    )
    
    professionals_aptos_names = serializers.StringRelatedField(
        many=True,
        source='professionals_aptos', # Mapeia para o campo real do modelo
        read_only=True 
    )
    
    class Meta:
        model = Service
        fields = ('id', 'name', 'minutes_duration', 'value', 'professionals_aptos', 'professionals_aptos_names')

        
class ClientSerializer(serializers.ModelSerializer):
    # O salão é injetado automaticamente pelo ViewSet, não precisa aparecer aqui
    class Meta:
        model = Client
        fields = ('id', 'name', 'phone_whatsap', 'email')


class SchedulingSerializer(serializers.ModelSerializer):
    # Campos de leitura para exibir o nome em vez dos IDs
    client_name = serializers.CharField(source='client.name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    professional_name = serializers.CharField(source='professional.name', read_only=True)
    
    # Campo para receber o ID do Salão, mas será setado internamente
    barbershop_name = serializers.CharField(source='barbershop.name', read_only=True)

    class Meta:
        model = Scheduling
        fields = (
            'id', 'date_hour_init', 'date_hour_end', 'status',
            'client', 'client_name', 'service', 'service_name', 'professional', 
            'professional_name', 'barbershop', 'barbershop_name',
        )
        # O cliente, serviço e profissional devem ser IDs para a criação
        read_only_fields = ('date_hour_end', 'status')

    # A validação principal ocorre aqui antes de salvar
    def validate(self, data):
        data = super().validate(data)
        
        # 1. Recuperar a duração do serviço E calcular o horário de fim (já está aqui, o que é ótimo)
        service = data['service']
        minutes_duration = service.minutes_duration
        init = data['date_hour_init']
        end = init + timedelta(minutes=minutes_duration)
        data['date_hour_end'] = end
        
        # 2. VERIFICAÇÃO DE CONFLITO (já está aqui)
        # ... (sua lógica de conflito)
        professional = data['professional']
        instance = self.instance
        conflits = Scheduling.objects.filter(
            professional=professional,
            date_hour_init__lt=end,
            date_hour_end__gt=init,
        )
        if instance:
            conflits = conflits.exclude(pk=instance.pk)
        
        if conflits.exists():
            raise serializers.ValidationError(
                {"date_hour_init": f"O profissional {professional.name} já tem um agendamento neste horário."}
            )

        return data
    
    # Sobrescrever o create para INJETAR o valor do serviço no validated_data ANTES de salvar
    def create(self, validated_data):
        # 1. LÓGICA CONCISA: Injetar o valor do Serviço no campo initial_value
        service = validated_data.get('service')
        if service:
            # Atribui o valor do Serviço ao Agendamento
            validated_data['initial_value'] = service.value 
        
        # 2. Salva a instância (o date_hour_end já foi calculado no validate)
        return super().create(validated_data)