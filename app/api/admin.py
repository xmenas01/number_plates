from django.contrib import admin
from api.models import NumberPlate, CarModel 
from django import forms

@admin.register(NumberPlate)
class NumberPlateAdmin(admin.ModelAdmin):
    list_display = [f.name for f in NumberPlate._meta.fields] 


class CarModelForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     self.request = kwargs.pop('request', None)
    #     super().__init__(*args, **kwargs)

    class Meta:
        model = CarModel 
        fields = "__all__"

    def clean(self):
        super().clean()
        manufacturer = self.cleaned_data.get('manufacturer')
        model = self.cleaned_data.get('model')
        if not self.initial or 'manufacturer' in self.changed_data or 'model' in self.changed_data:
            if CarModel.objects.filter(manufacturer=manufacturer, model=model).exists():
                raise forms.ValidationError("Duplicate exists of combined fields: manufacturer and model")
        return self.cleaned_data

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    form = CarModelForm
    list_display = [f.name for f in CarModel._meta.fields] 