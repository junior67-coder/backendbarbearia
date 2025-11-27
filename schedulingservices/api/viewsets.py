from rest_framework import viewsets, permissions
from authentication.models import BarberShop
from schedulingservices.models import Client, Professional, Scheduling, Service

from .serializers import ClientSerializer, ProfessionalSerializer, SchedulingSerializer, ServiceSerializer

from django.shortcuts import get_object_or_404


class MultiTenantModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    # 1. Filtra o Queryset para mostrar APENAS os dados do Salão do Usuário Logado
    def get_queryset(self):
        # Todos os modelos em servicos_agendamento têm o campo 'salao'
        return self.queryset.filter(barbershop__owner=self.request.user)
    
    # 2. Injeta o Salão (tenant) no objeto ANTES de salvar (criação)
    def perform_create(self, serializer):
        # O Salão é obtido através do usuário logado (proprietario)
        barbershop = get_object_or_404(BarberShop, owner=self.request.user)
        serializer.save(barbershop=barbershop)
        
        
class ProfessionalViewSet(MultiTenantModelViewSet):
    """Permite listar, criar, atualizar e deletar Profissionais, filtrado pelo Salão logado."""
    queryset = Professional.objects.all()
    serializer_class = ProfessionalSerializer
    
    
class ServiceViewSet(MultiTenantModelViewSet):
    """Permite listar, criar, atualizar e deletar Serviços, filtrado pelo Salão logado."""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    
    # Sobrescreve perform_create para lidar com o M2M (profissionais_aptos) após salvar
    def perform_create(self, serializer):
        # 1. Injeta o salão e salva a instância principal
        super().perform_create(serializer)
        
        # 2. Lógica para filtrar o ManyToMany (profissionais_aptos) pelo Salão
        # Se o serializer tem dados de 'profissionais_aptos', garantimos que eles pertencem ao Salão
        if 'professionals_aptos' in self.request.data:
            professionals_ids = self.request.data['professionals_aptos']
            # Filtra os IDs fornecidos para garantir que pertencem ao salão atual
            professionals_of_barbershop = Professional.objects.filter(barbershop__owner=self.request.user, id__in=professionals_ids)
            serializer.instance.professionals_aptos.set(professionals_of_barbershop)
            
            
class ClientViewSet(MultiTenantModelViewSet):
    """Permite listar, criar, atualizar e deletar Clientes, filtrado pelo Salão logado."""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


# --- Novo ViewSet: Agendamento ---
class ShedulingViewSet(MultiTenantModelViewSet):
    """Permite listar e criar Agendamentos, com verificação de conflito."""
    queryset = Scheduling.objects.all().order_by('date_hour_init') # Ordenação padrão
    serializer_class = SchedulingSerializer
    
    # Sobrescreve perform_create para injetar o Salão, tal como no MultiTenantModelViewSet
    def perform_create(self, serializer):
        # 1. Obter a instância do Salão
        barbershop = get_object_or_404(BarberShop, owner=self.request.user)
        
        # 2. Injetar o Salão e salvar a instância
        # Nota: O data_hora_fim já está em validated_data, graças ao método validate do serializer
        serializer.save(barbershop=barbershop)
