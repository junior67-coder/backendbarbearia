from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .serializers import RescheduleSuggestionSerializer
from schedulingservices.models import Scheduling, Client, Service
from intelligence.models import FrequencySuggestion 
from authentication.models import BarberShop 


class RescheduleSuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retorna a lista de clientes para os quais a IA sugere reagendamento.
    Acesso restrito ao proprietário da barbearia (Multi-Tenant).
    """
    serializer_class = RescheduleSuggestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
       # 1. Encontre a barbearia do usuário logado
        try:
            barbershop = get_object_or_404(BarberShop, owner=user)
        except BarberShop.DoesNotExist:
            return [] # Nenhuma barbearia encontrada para o usuário

        today = timezone.now().date()
        
        # 2. Encontre a última data de conclusão para cada cliente/serviço
        # Encontre o último agendamento 'Concluido' (Concluído)
        last_schedulings = Scheduling.objects.filter(
            barbershop=barbershop,
            status='Concluido' 
        ).values('client', 'service').annotate(
            last_service_date=Max('date_hour_init')
        )
        
        # 3. Avalie cada cliente/serviço para ver se está dentro da janela de sugestão
        candidate_suggestions = []
        
        for item in last_schedulings:
            try:
                # Recupere a regra de sugestão de frequência para o serviço
                rule = FrequencySuggestion.objects.get(
                    barbershop=barbershop,
                    service_id=item['service']
                )
            except FrequencySuggestion.DoesNotExist:
                continue 
            
            last_date = item['last_service_date'].date()
            days_passed = (today - last_date).days
            
            ideal_days = rule.ideal_return_days
            tolerance_days = rule.anticipation_tolerance_days
            
            # Calcule a janela de sugestão de reagendamento com base na regra de sugestão de frequência para o serviço 
            min_suggestion_days = ideal_days - tolerance_days
            
            if min_suggestion_days <= days_passed <= ideal_days:
                # O cliente/serviço está dentro da janela de sugestão
                candidate_suggestions.append({
                    'client__id': item['client'],
                    'client__name': Client.objects.get(id=item['client']).name,
                    'service__name': Service.objects.get(id=item['service']).name,
                    'last_service_date': item['last_service_date'],
                    'days_since_service': days_passed,
                    'days_to_suggest': ideal_days - days_passed
                })
                
        # 4. Retorne a lista de sugestões candidatas para reagendamento de clientes
        return candidate_suggestions
