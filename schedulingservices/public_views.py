from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from datetime import timedelta, datetime, time, date
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from authentication.models import BarberShop
from schedulingservices.api.serializers import SchedulingSerializer, ServiceSerializer
from .models import Client, Professional, Service, Scheduling


class PublicSchedulingAPI(APIView):
    """
    API para clientes externos (não logados) visualizarem dados do salão e agendarem.
    Acesso filtrado pelo 'link_agendamento' (slug).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, link_slug, format=None):
        """
        Retorna os Serviços e Profissionais aptos de um salão específico.
        """
        try:
            # 1. Encontra o Salão pelo slug (link_agendamento)
            barbershop = BarberShop.objects.get(scheduling_link=link_slug, ative=True)
        except BarberShop.DoesNotExist:
            return Response({"detail": "Salão não encontrado ou inativo."}, status=status.HTTP_404_NOT_FOUND)

        # 2. Busca todos os serviços ativos daquele salão
        services = Service.objects.filter(barbershop=barbershop)
        serializer = ServiceSerializer(services, many=True)

        return Response({
            "barbershop_name": barbershop.name,
            "services": serializer.data
        })
    
    # Próxima etapa: O método POST para criar o Agendamento
    def post(self, request, link_slug, format=None):
        """
        Cria um novo agendamento para o cliente.
        """
        try:
            barbershop = BarberShop.objects.get(link_agendamento=link_slug, ative=True)
        except BarberShop.DoesNotExist:
            return Response({"detail": "Salão não encontrado ou inativo."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        
        # 1. Encontra ou Cria o Cliente (Baseado no telefone/nome)
        # Assume que o cliente fornece nome e telefone
        client_data = {
            'barbershop': barbershop,
            'name': data.get('client_name'),
            'phone_whatsap': data.get('client_phone'),
            'email': data.get('client_email'),
        }
        
        # Tenta encontrar cliente existente pelo telefone e salão
        client, created = Client.objects.get_or_create(
            barbershop=barbershop,
            phone_whatsap=client_data['phone_whatsap'],
            defaults=client_data # Usa estes dados se for criado
        )
        
        # 2. Prepara os dados do Agendamento
        scheduling_data = {
            'client': client.id,
            'service': data.get('service_id'),
            'professional': data.get('professional_id'),
            'date_hour_init': data.get('date_hour_init'),
            # 'barbershop' será injetado abaixo
        }
        
        # 3. Serialização e Validação
        serializer = SchedulingSerializer(data=scheduling_data)
        
        if serializer.is_valid():
            # Injeta o barbershop antes de salvar (segurança)
            scheduling = serializer.save(barbershop=barbershop)
            
            # Envio de notificação (Lembrete de Email/WhatsApp - futura integração)
            
            return Response({
                "detail": "Agendamento criado com sucesso.",
                "scheduling_id": scheduling.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublicAvailableTimesAPI(APIView):
    """
    Retorna os horários disponíveis para um profissional em uma data e serviço específicos.
    Endpoint: /api/v1/public/<slug>/available-times/?professional_id=X&service_id=Y&date=YYYY-MM-DD
    """
    
    permission_classes = [permissions.AllowAny]

    def get(self, request, link_slug, format=None):
        # 1. Obter e validar parâmetros (JSON ou Query Params)
        try:
            barbershop = BarberShop.objects.get(scheduling_link=link_slug, ative=True)
            
            # Parâmetros esperados na URL:
            professional_id = request.query_params.get('professional_id')
            service_id = request.query_params.get('service_id')
            date_str = request.query_params.get('date')

            if not all([professional_id, service_id, date_str]):
                return Response({"detail": "professional_id, service_id e date são obrigatórios."}, 
                                status=status.HTTP_400_BAD_REQUEST)

            professional = get_object_or_404(Professional, id=professional_id, barbershop=barbershop)
            service = get_object_or_404(Service, id=service_id, barbershop=barbershop)
            
            # Converte a string de data para objeto date
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            service_duration = service.minutes_duration

        except Exception as e:
            # Captura erros de DataNotFound (404) ou conversão de data (ValueError)
            return Response({"detail": f"Erro de validação ou recurso não encontrado: {e}"}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # 2. Definir Horário de Trabalho (MVP Simples: 9h às 18h)
        # Importante: Usar a timezone correta
        current_tz = timezone.get_current_timezone()
        
        # Horário de Início/Fim do dia de trabalho
        start_time_of_day = time(9, 0)
        end_time_of_day = time(18, 0)
        
        # Datetime completo do início do trabalho
        start_datetime = datetime.combine(target_date, start_time_of_day, tzinfo=current_tz)
        # Datetime do Fim do dia (para o loop)
        end_datetime = datetime.combine(target_date, end_time_of_day, tzinfo=current_tz)

        # 3. Buscar Agendamentos Ocupados
        occupied_times = Scheduling.objects.filter(
            professional=professional,
            date_hour_init__date=target_date,
            status__in=['Pendente', 'Confirmado'] # Apenas agendamentos que ocupam o tempo
        ).order_by('date_hour_init').values('date_hour_init', 'date_hour_end')

        # 4. Gerar e Filtrar Slots Livres
        available_slots = []
        current_slot_start = start_datetime
        step = timedelta(minutes=service_duration) # Avança pelo tempo de duração do SERVIÇO

        # Loop enquanto o slot atual (início) mais a duração do serviço não exceder o fim do dia
        while current_slot_start + timedelta(minutes=service_duration) <= end_datetime:
            slot_end = current_slot_start + timedelta(minutes=service_duration)
            is_available = True
            
            # Verifica se o slot atual colide com qualquer agendamento existente
            for occupied in occupied_times:
                occupied_start = occupied['date_hour_init']
                occupied_end = occupied['date_hour_end']
                
                # Regra de Conflito: O novo slot se sobrepõe a um agendamento existente
                # Se (Novo Início < Fim Existente) E (Novo Fim > Início Existente) -> CONFLITO
                if (current_slot_start < occupied_end) and (slot_end > occupied_start):
                    is_available = False
                    
                    # Se há conflito, pulamos para o fim do agendamento ocupado.
                    # Adicionamos um minuto para garantir que a próxima iteração seja após o término.
                    current_slot_start = occupied_end + timedelta(minutes=1)
                    break # Sai do loop 'occupied_times' e volta para o 'while' principal

            if is_available:
                # Se não houve conflito, adiciona o slot e avança o slot para o próximo passo
                available_slots.append(current_slot_start.strftime('%H:%M'))
                current_slot_start += step # Avança pelo tempo de duração do SERVIÇO
            
            # Se 'is_available' foi False, o 'current_slot_start' já foi avançado pelo 'break'.

        # 5. Retorno
        return Response({
            "professional_name": professional.name,
            "date": date_str,
            "service_duration_minutes": service_duration,
            "available_slots": available_slots
        })
