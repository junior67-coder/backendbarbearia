from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from authentication.api.viewsets import BarberShopViewSet
from schedulingservices.api.viewsets import ProfessionalViewSet, ServiceViewSet


router = DefaultRouter()

# Rotas da API principal (versão 1)
router.register(r'salao', BarberShopViewSet)
router.register(r'servico', ServiceViewSet)
router.register(r'profissional', ProfessionalViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    # Rotas da API principal (versão 1)
    path('api/v1/', include(router.urls)),
    
    # Adicionar rotas de autenticação do DRF (login/logout)
    path('api/v1/auth/', include('rest_framework.urls'))
]
