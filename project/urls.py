from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView, # View para obter o token (Login)
    TokenRefreshView, # View para renovar o token
)

from rest_framework.routers import DefaultRouter
from authentication.api.viewsets import BarberShopViewSet
from schedulingservices.api.viewsets import ProfessionalViewSet, ServiceViewSet, ClientViewSet, SchedulingViewSet
from intelligence.api.viewsets import RescheduleSuggestionViewSet
from schedulingservices.api.viewsets import ClientViewSet, ProfessionalViewSet, ServiceViewSet, ShedulingViewSet

from schedulingservices.public_views import PublicSchedulingAPI, PublicAvailableTimesAPI

router = DefaultRouter()

# Rotas da API principal (versão 1)
router.register(r'salao', BarberShopViewSet)
router.register(r'servico', ServiceViewSet)
router.register(r'profissional', ProfessionalViewSet)
router.register(r'clientes', ClientViewSet)
router.register(r'agendamentos', SchedulingViewSet)
router.register(r'agendamentos', ShedulingViewSet)
router.register(r'ai-sugestoes', RescheduleSuggestionViewSet, basename='ai-suggestions')



urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/v1/', include([
        
        # 1. Rotas do Router (Seguras: /api/v1/salao/, /api/v1/servico/, etc.)
        path('', include(router.urls)),
        
        # 2. Rotas de Autenticação (Login/Refresh)
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        
        # 3. Rotas Públicas (Agendamento, que não usam Token)
        path('public/<slug:link_slug>/', PublicSchedulingAPI.as_view(), name='public-scheduling'),
        path('public/<slug:link_slug>/available-times/', PublicAvailableTimesAPI.as_view(), name='public-available-times'),
        
        # 4. Rota de login do DRF (útil para browsable API)
        path('auth/', include('rest_framework.urls')),
    ])),
]

