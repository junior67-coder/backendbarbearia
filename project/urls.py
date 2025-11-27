from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from authentication.api.viewsets import BarberShopViewSet
from schedulingservices.api.viewsets import ClientViewSet, ProfessionalViewSet, ServiceViewSet, ShedulingViewSet

from schedulingservices.public_views import PublicSchedulingAPI, PublicAvailableTimesAPI

router = DefaultRouter()

# Rotas da API principal (versão 1)
router.register(r'salao', BarberShopViewSet)
router.register(r'servico', ServiceViewSet)
router.register(r'profissional', ProfessionalViewSet)
router.register(r'clientes', ClientViewSet)
router.register(r'agendamentos', ShedulingViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    # Rotas da API principal (versão 1)
    path('api/v1/', include(router.urls)),
    
    # 1. Rota para Agendar (POST) e Consultar Serviços (GET)
    # Ex: GET ou POST para /api/v1/public/salao-nova-unidade/
    path('public/<slug:link_slug>/', PublicSchedulingAPI.as_view(), name='public-scheduling'),
    
    # 2. Rota para Consultar Horários Livres (GET)
    # Ex: GET para /api/v1/public/salao-nova-unidade/available-times/?professional_id=X...
    path('public/<slug:link_slug>/available-times/', PublicAvailableTimesAPI.as_view(), name='public-available-times'),
    
    # Adicionar rotas de autenticação do DRF (login/logout)
    path('api/v1/auth/', include('rest_framework.urls'))
]
