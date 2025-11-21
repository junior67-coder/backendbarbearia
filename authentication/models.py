from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class BarberShop(models.Model):
    """Representa o salão (o 'tenant' principal) no sistema."""
    
    PLANO_CHOICES = (
        ('Basico', 'Plano Básico'),
        ('Pro', 'Plano Pro'),
        ('Premium', 'Plano Premium'),
    )

    name = models.CharField('Nome', max_length=200)
    cnpj = models.CharField(max_length=14, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    plans = models.CharField(max_length=50, choices=PLANO_CHOICES, default='Basico')
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='salao_gerenciado')
    scheduling_link = models.SlugField(max_length=100, unique=True, editable=False)
    active = models.BooleanField(default=True)
    date_register = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Salão'
        verbose_name_plural = "Salões"
        
    def __str__(self):
        return self.name
