from rest_framework import serializers

from schedulingservices.models import Scheduling, Professional, Service, Client
from authentication.models import BarberShop

from datetime import timedelta


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
    barbershop = serializers.CharField(source='barbershop.name', read_only=True)

    class Meta:
        model: Scheduling
        fields = (
            'id', 'date_hour_init', 'date_hour_end', 'confirmado', 'cancelado',
            'client', 'client_name', 'service', 'service_name', 'professional',
            'professional_name', 'barbershop', 'barbershop.name'
        )
        # O cliente, serviço e profissional devem ser IDs para a criação
        read_only_fields = ('date_hour_end', 'confirmado', 'cancelado',)

    # A validação principal ocorre aqui antes de salvar
    def validate(self, data):
        data = super().validate(data)

        # 1. Recuperar a duração do serviço
        service = data['service']
        minutes_duration = service.minutes_duration

        # 2. Calcular o horário de fim
        init = data['date_hour_init']
        end = init + timedelta(minutes=minutes_duration)

        # Injetar o fim calculado de volta nos dados
        data['date_hour_end'] = end

        # Verica se há conflito
        professional = data['professional']

        instance = self.instance

        conflits = Scheduling.objects.filter(
            professional=professional,
            # Verifica se o período solicitado se sobrepõe a qualquer agendamento existente:
            # Novo início está antes do fim existente E Novo fim está depois do início existente
            date_hour_init__lt=end,
            date_hour_end__gt=init,
        )

        if instance:
            # Se for update, exclui a instância atual da lista de conflitos
            conflits = conflits.exclude(pk=instance.pk)

        if conflits.exists():
            raise serializers.ValidationError(
                {'date_hour_init': f'O profissional {professional.name} já tem um serviço nesse horário!'}
            )
        
        return data

    
    # Sobrescrever o create para garantir que o data_hora_fim seja salvo
    def create(self, validated_data):
        return super().create(validated_data)
        