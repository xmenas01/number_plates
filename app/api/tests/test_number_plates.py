from django.test import TestCase
# from django.urls import reverse
from rest_framework.reverse import reverse

from rest_framework.test import APIClient
from rest_framework import status
from api.models import NumberPlate, CarModel


PLATE_URL = reverse('numberplate-list')

class NumberPlateTest(TestCase):
    """ Test the number plate API """
    def setUp(self):
        self.client = APIClient()
        self.payload = {
            'number' : 'ANJ519',
            'owner' : 'Peter',
            'car_model' : {
                'manufacturer': 'porsche',
                'model': '911'
            }
        }

    def prepopulate_db(self):
        car_model_rec = {
            'manufacturer': 'porsche',
            'model': '911'
        }
        car_model = CarModel.objects.create(**car_model_rec)
        number_plate_rec = {
            'number' : 'ANJ519',
            'owner' : 'Peter',
            'car_model' : car_model
        }
        NumberPlate(**number_plate_rec).save()

    def test_create_number_plate(self):
        """ Test creation of number plate record with valid payload is successful""" 
        resp = self.client.post(PLATE_URL, self.payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        car_model = CarModel.objects.get(**resp.data.get('car_model'))
        resp.data['car_model'] = car_model
        self.assertTrue(NumberPlate.objects.filter(**resp.data).exists())

    def test_number_plates_duplicaton(self):
        """ Test creation of number plate that already exists, fails """
        self.prepopulate_db()
        resp = self.client.post(PLATE_URL, self.payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_number_plate_validation(self):
        """ Test creation of number plate format, fails"""
        payload = {
            'number' : 'ANJC519',
            'owner' : 'Peter'
        }
        resp = self.client.post(PLATE_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
