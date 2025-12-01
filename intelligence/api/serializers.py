from rest_framework import serializers

class RescheduleSuggestionSerializer(serializers.Serializer):
    """Returns the necessary data for the manager to act on the suggestion."""
    
    client_id = serializers.IntegerField(source='client__id')
    client_name = serializers.CharField(source='client__name')
    service_name = serializers.CharField(source='service__name')
    last_service_date = serializers.DateTimeField()
    days_since_service = serializers.IntegerField()
    days_to_suggest = serializers.IntegerField()