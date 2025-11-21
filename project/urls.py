from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    # Rotas da API principal (versão 1)
    path('api/v1/', include('authentication.urls')),
    
    # Adicionar rotas de autenticação do DRF (login/logout)
    path('api/v1/auth/', include('rest_framework.urls'))
]
