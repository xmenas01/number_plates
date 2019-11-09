from django.test import TestCase
# from django.urls import reverse
from rest_framework.reverse import reverse

from rest_framework.test import APIClient
from rest_framework import status
from api.models import NumberPlate


PLATE_URL = reverse('numberplate-list')

class NumberPlateTest(TestCase):
    """ Test the number plate API """
    def setUp(self):
        self.client = APIClient()
        self.payload = {
            'number' : 'ANJ519',
            'owner' : 'Peter',
            'car_model' : 'porsche 911'
        }

    def test_create_number_plate(self):
        """ Test creation of number plate record with valid payload is successful""" 
        resp = self.client.post(PLATE_URL, self.payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(NumberPlate.objects.filter(**resp.data).exists())

    def test_number_plates_duplicaton(self):
        """ Test creation of number plate that already exists, fails """
        NumberPlate(**self.payload).save()
        resp = self.client.post(PLATE_URL, self.payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_number_plate_validation(self):
        """ Test creation of number plate format, fails"""
        payload = {
            'number' : 'ANJC519',
            'owner' : 'Peter',
            'car_model' : 'porsche 911'
        }
        resp = self.client.post(PLATE_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
