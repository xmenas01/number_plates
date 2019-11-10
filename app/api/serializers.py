import re

from rest_framework import serializers

from api.models import NumberPlate, CarModel
from api.tasks import task_car_model_get_picture

class CarModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarModel
        fields = ('manufacturer', 'model', 'image', 'ctask_status', 'ctask_message')
        read_only_fields = ('image', 'ctask_status', 'ctask_message')

class NumberPlateSerializer(serializers.ModelSerializer):
    car_model = CarModelSerializer(many=False, required=False)

    class Meta:
        model = NumberPlate
        fields = ('id','number', 'owner', 'car_model')
    
    def validate_number(self, value):
        """ Check that the number is contains three letters and three numbers. """
        if not re.match(r'\w{3}\d{3}', value):
            raise serializers.ValidationError("Plate number length should have 6 symbols "\
                "and contain of first three alphabetical letters follewed by three numbers. exmp.: ABC123")
        return value

    def create(self, validated_data):
        model = validated_data.pop('car_model', None)
        if model:
            if CarModel.objects.filter(**model).exists():
                #TODO: except for duplicate entries in cases when duplicate was created over admin portal
                validated_data['car_model'] = CarModel.objects.get(**model) 
            elif not all(value == "" for value in model.values()):
                model = {k:v.lower().strip() for (k,v) in model.items()}
                model_obj = CarModel.objects.create(**model)
                task_car_model_get_picture.delay(car_model_id=model_obj.id)
                validated_data['car_model'] = model_obj
        validated_data['number'] = validated_data['number'].upper()
        number_plate = NumberPlate.objects.create(**validated_data)
        return number_plate

    def update(self, instance, validated_data):
        instance.number = validated_data.get('number', instance.number)
        instance.owner = validated_data.get('owner', instance.owner)
        model = validated_data.pop('car_model', None)
        if model: 
            if CarModel.objects.filter(**model).exists():
                instance.car_model = CarModel.objects.get(**model) 
            elif not all(value == "" for value in model.values()):
                model = {k:v.lower().strip() for (k,v) in model.items()}
                model_obj = CarModel.objects.create(**model)
                task_car_model_get_picture.delay(car_model_id=model_obj.id)
                validated_data['car_model'] = model_obj
                instance.car_model = validated_data.get('car_model')
            else:
                instance.car_model = None
        else: 
            instance.car_model = None
        instance.save()
        return instance 