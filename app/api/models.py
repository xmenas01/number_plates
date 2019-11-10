from django.db import models

class NumberPlate(models.Model):
    """ Car number plates """
    number = models.CharField(max_length=6, unique=True)
    owner = models.CharField(max_length=255)
    car_model = models.ForeignKey('CarModel', related_name='number_plates', blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.number


CTASK_STATUS_CHOICE = [
    ('IN PROGRESS', 'In progress'),
    ('SUCCESS', 'Success'),
    ('FAIL', 'Fail'),
]

class CarModel(models.Model):
    """ Car models with pictures """
    manufacturer = models.CharField('Car Manufacturer', max_length=255, blank=True)
    model = models.CharField('Car Model', max_length=255, blank=True)
    image = models.ImageField(blank=True, upload_to='images/')
    ctask_status = models.CharField('Celery task state', max_length=255, choices=CTASK_STATUS_CHOICE, default='IN PROGRESS')
    ctask_message = models.CharField('Celery message', max_length=255, blank=True)

    def __str__(self):
        return f'{self.manufacturer} {self.model}'.strip()