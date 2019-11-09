from django.db import models

class NumberPlate(models.Model):
    """ Car number plates """
    number = models.CharField(max_length=6)
    owner = models.CharField(max_length=255)
    car_model = models.CharField(max_length=255)

    def __str__(self):
        return self.number

