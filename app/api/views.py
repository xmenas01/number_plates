from django.shortcuts import render

from rest_framework import viewsets
from api.serializers import NumberPlateSerializer
from api.models import NumberPlate


class NumberPlateViewSet(viewsets.ModelViewSet):
    serializer_class = NumberPlateSerializer
    queryset = NumberPlate.objects.all()