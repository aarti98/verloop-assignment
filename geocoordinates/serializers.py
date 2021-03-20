from rest_framework import serializers

OUTPUT_CHOICES = ['json', 'xml']


class AddressToCoordinatesSerializer(serializers.Serializer):
    address = serializers.CharField()
    output_format = serializers.ChoiceField(
        choices=OUTPUT_CHOICES
    )
