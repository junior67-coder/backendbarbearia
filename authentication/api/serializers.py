from rest_framework import serializers
from authentication.models import BarberShop
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


# Serializer para o modelo User, usado dentro do Salão
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',  'last_name',)
        read_only_fields = ('id', )


class BarberShopSerializer(serializers.ModelSerializer):
    # Relacionamento de leitura: Exibe o usuário proprietário
    owner = UserSerializer(read_only=True)

    # Campo para receber a senha no momento da criação
    password_owner = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = BarberShop
        fields = (
            'id', 'name', 'cnpj', 'email', 'plans', 'scheduling_link', 'active', 'owner',
            'password_owner',
        )

    def create(self, validated_data):
        # Boas Práticas: Criar o Usuário antes de criar o Salão
        password = validated_data.pop('password_owner')

        # O username será o email de contato para simplificar
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=password
        )
        
        # 1. Cria o link de agendamento (Ex: salao-nova-unidade)
        validated_data['scheduling_link'] = slugify(validated_data['name'])

        # 2. Cria o Salão, associando o novo usuário como proprietário
        barbershop = BarberShop.objects.create(owner=user, **validated_data)

        return barbershop
    
    