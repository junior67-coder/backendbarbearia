from django.db import models
from schedulingservices.models import Service 
from authentication.models import BarberShop 


class FrequencySuggestion(models.Model):
    """Define o horário ideal de retorno para um atendimento específico na barbearia."""
    
    barbershop = models.ForeignKey(BarberShop, on_delete=models.CASCADE, related_name='frequencies')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='suggested_frequency')
    
    ideal_return_days = models.IntegerField(
        help_text="Número de dias após o último atendimento que o cliente idealmente deveria retornar (ex.: 30 dias para Corte de Cabelo).",
        default=30
    )
    
    # Tolerância antes de enviar a sugestão (ex.: Começar a sugerir 5 dias antes do ideal)
    anticipation_tolerance_days = models.IntegerField(default=5) 
    
    class Meta:
        unique_together = ('barbershop', 'service')
        verbose_name = "Sugestão de Frequência"
        
    def __str__(self):
        return f"{self.service.name}: {self.ideal_return_days} days"
