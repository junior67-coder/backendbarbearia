from django.db import models
from django.core.validators import MinValueValidator
from datetime import timedelta

from authentication.models import BarberShop

# Create your models here.

STATUS_CHOICES = (
    ('Pendente', 'Pendente'),
    ('Confirmado', 'Confirmado'),
    ('Concluido', 'Concluído'),
    ('Cancelado', 'Cancelado'),
)


# Class de profissionais
class Professional(models.Model):
    """Representa o profissional/prestador de serviço."""
    barbershop = models.ForeignKey(BarberShop, on_delete=models.CASCADE, related_name='profissionals', verbose_name='Salão')
    name = models.CharField('Nome', max_length=200)
    phone = models.CharField('Telefone', max_length=20)
    commission_standard = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0.40,
        validators=[MinValueValidator(0.00)],
        verbose_name='Comissão Padrao'
    )
    ative = models.BooleanField(default=True)

    
    class Meta:
        verbose_name = 'Profissional'
        verbose_name_plural = "Profissionais"
        unique_together = ('barbershop', 'name')
        
        
    def __str__(self):
        return f"{self.name} ({self.barbershop.name})"
    

# Class de serviços
class Service(models.Model):
    """Representa um serviço oferecido pelo salão."""
    barbershop = models.ForeignKey(BarberShop, on_delete=models.CASCADE, related_name='services', verbose_name='Salão')
    name = models.CharField('Nome', max_length=200)
    minutes_duration = models.IntegerField(
        validators=[MinValueValidator(5)],
        help_text='Tempo médio em minutos para execução do serviço',
    )
    value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)], verbose_name='Valor')
    professionals_aptos = models.ManyToManyField(Professional, related_name='services_aptos', verbose_name='Profissionais aptos')
    
    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = "Serviços"
        unique_together = ('barbershop', 'name')
        
    def __str__(self):
        return self.name


# Class de cliente
class Client(models.Model):
    """Representa o cliente cadastrado para fins de CRM e agendamento."""
    barbershop = models.ForeignKey(BarberShop, on_delete=models.CASCADE, related_name='clients', verbose_name='Salão')
    name = models.CharField('Nome', max_length=200)
    phone_whatsap = models.CharField('Telefone', max_length=20)
    email = models.EmailField('Email', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = "Clientes"
        unique_together = ('barbershop', 'phone_whatsap')
        
    def __str__(self):
        return self.name
    

# Class de agendamento
class Scheduling(models.Model):
    """Registro de um agendamento específico."""
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='schedulings', verbose_name='Cliente')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='schedulings', verbose_name='Serviço')
    professional = models.ForeignKey(Professional, on_delete=models.PROTECT, related_name='schedulings', verbose_name='Profissional')
    date_hour_init = models.DateTimeField(verbose_name='Data de inicio')
    date_hour_end = models.DateTimeField(verbose_name='Data de fim', blank=True, null=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='Pendente')
    initial_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Valor Inicial')
    
    
    def save(self, *args, **kwargs):
        # Calcula data_hora_fim baseado na duração do Serviço
        if self.service and self.date_hour_init and not self.date_hour_end:
            duration = self.service.minutes_duration
            self.date_hour_end = self.date_hour_init + timedelta(minutes=duration)
            
        if self.service and self.initial_value == 0.00:
            self.initial_value = self.service.velue
            
        super().save(*args, **kwargs)
        
    class Meta:        
        verbose_name = 'Agendamento'
        verbose_name_plural = "Agendamentos"
        unique_together = ['date_hour_init']
