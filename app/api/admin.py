from django.contrib import admin
from api.models import NumberPlate, CarModel 
from django import forms

@admin.register(NumberPlate)
class NumberPlateAdmin(admin.ModelAdmin):
    list_display = [f.name for f in NumberPlate._meta.fields] 

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = [f.name for f in CarModel._meta.fields] 
