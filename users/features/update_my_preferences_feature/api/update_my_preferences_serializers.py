from rest_framework import serializers


class UpdatePreferencesInputSerializer(serializers.Serializer):
    experience_level = serializers.CharField(required=False)
    primary_goal = serializers.CharField(required=False)
    training_frequency_per_week = serializers.IntegerField(required=False)
    available_equipment = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
