from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from authentication.models import BarberShop
from authentication.api.serializers import BarberShopSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permissão customizada para permitir que apenas o proprietário edite."""

    def has_object_permission(self, request, view, obj):
        # Permite GET, HEAD, OPTIONS (Métodos seguros) para qualquer usuário autenticado
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permite a escrita (PUT, PATCH, DELETE) apenas se o usuário for o proprietário
        return obj.owner == request.user
    

class BarberShopViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite o Salão ser visualizado ou editado pelo proprietário.
    A criação (POST) está aberta para novos registros.
    """

    queryset = BarberShop.objects.all()
    serializer_class = BarberShopSerializer

    # Definindo a permissão
    def get_permissions(self):
        # Se for um POST (Criação de novo Salão), não exige autenticação
        if self.action == ('create'):
            return [permissions.AllowAny()]
        # Para todas as outras ações (GET, PUT, DELETE), exige autenticação e a permissão customizada
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]

    # Boas Práticas: Multi-Tenancy - Filtra o queryset para mostrar apenas o salão do usuário logado
    def get_queryset(self):
        # Se o usuário não estiver autenticado (ou for POST), retorna o queryset completo (para o 'create' funcionar)
        if not self.request.user.is_authenticated:
            return BarberShop.objects.none()
        
        # Filtra para retornar apenas o Salão que o usuário logado gerencia
        return self.queryset.filter(owner=self.request.user)
