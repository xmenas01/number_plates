from rest_framework import serializers

from api.models import NumberPlate

class NumberPlateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberPlate
        fields = '__all__' 