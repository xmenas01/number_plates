from rest_framework import serializers

from api.models import NumberPlate, CarModel
from api.tasks import task_car_model_get_picture

class CarModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarModel
        fields = ('manufacturer', 'model', 'image', 'ctask_status', 'ctask_message')
        read_only_fields = ('image', 'ctask_status', 'ctask_message')

class NumberPlateSerializer(serializers.ModelSerializer):
    car_model = serializers.PrimaryKeyRelatedField(many=False, allow_null=True, queryset=CarModel.objects.all())

    class Meta:
        model = NumberPlate
        fields = ('id','number', 'owner', 'car_model')


#     class Meta:
#         model = NumberPlate
#         fields = ('id','number', 'owner', 'car_model')
# class CarModelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CarModel
#         fields = ('manufacturer', 'model', 'image', 'ctask_status', 'ctask_message')
#         read_only_fields = ('image', 'ctask_status', 'ctask_message')

# class NumberPlateSerializer(serializers.ModelSerializer):
#     car_model = CarModelSerializer(many=False, required=False)

#     class Meta:
#         model = NumberPlate
#         fields = ('id','number', 'owner', 'car_model')
    
#     def validate_car_model(self, model):
#         """ Check if we need create car_model or not """
#         if not model.get('manufacturer', None):
#             model['manufacturer'] = ''
#         if not model.get('model', None):
#             model['model'] = ''
#         if CarModel.objects.filter(**model).exists():
#             model = CarModel.objects.get(**model) 
#             return model
#         if not all(value == "" for value in model.values()):
#             model = {k:v.lower().strip() for (k,v) in model.items()}
#             model_obj = CarModel.objects.create(**model)
#             task_car_model_get_picture.delay(car_model_id=model_obj.id)
#             model = model_obj
#             return model
#         return None

#     def create(self, validated_data):
#         validated_data['number'] = validated_data['number'].upper()
#         number_plate = NumberPlate.objects.create(**validated_data)
#         return number_plate

#     def update(self, instance, validated_data):
#         instance.number = validated_data.get('number', instance.number)
#         instance.owner = validated_data.get('owner', instance.owner)
#         model = validated_data.get('car_model', None)
#         if model:
#             instance.car_model = validated_data.get('car_model', instance.car_model)
#         else:
#             instance.car_model = None
#         instance.save()
#         return instance 
