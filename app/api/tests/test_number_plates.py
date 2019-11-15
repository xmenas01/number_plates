from unittest.mock import patch
import json

from django.test import TestCase
from rest_framework.reverse import reverse

from rest_framework.test import APIClient
from rest_framework import status
from api.models import NumberPlate, CarModel
from api.tasks import task_car_model_cb, task_car_model_get_picture


PLATE_URL = reverse('numberplate-list')

class NumberPlateTest(TestCase):
    """ Test the number plate API """
    def setUp(self):
        self.client = APIClient()
        self.payload = {
            'number': 'ANJ519',
            'owner': 'Peter',
            'car_model': {
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
        car_model_rec = {
            'manufacturer': 'porsche',
            'model': 'rs'
        }
        car_model = CarModel.objects.create(**car_model_rec)
        number_plate_rec = {
            'number': 'ANJ519',
            'owner': 'Peter',
            'car_model': car_model
        }
        NumberPlate(**number_plate_rec).save()

    @patch('api.tasks.get_image')
    @patch('api.tasks.task_car_model_get_picture.retry')
    def test_task_car_model_get_picture_exception(self, mock_retry, mock_get_image):
        self.prepopulate_db()
        mock_get_image.side_effect = Exception('shit happens') 
        self.assertEqual(task_car_model_get_picture(car_model_id=1), 'FAILED')
        mock_get_image.assert_called_with('porsche 911')
        car_model = CarModel.objects.get(pk=1)
        self.assertEqual(car_model.ctask_status, 'FAILED')
        self.assertEqual(car_model.ctask_message, 'Failed to get image of car model porsche 911. Due to: Exception:shit happens')

    @patch('api.tasks.get_image')
    def test_task_car_model_get_picture(self, mock_get_image):
        self.prepopulate_db()
        mock_get_image.return_value = 'images/porsche 911.jpg'
        self.assertEqual(task_car_model_get_picture(car_model_id=1), 'SUCCESS')
        mock_get_image.assert_called_with('porsche 911')
        car_model = CarModel.objects.get(pk=1)
        self.assertEqual(car_model.image, 'images/porsche 911.jpg')
        self.assertEqual(car_model.ctask_status, 'SUCCESS')

    @patch('api.tasks.task_car_model_get_picture.delay')
    def test_task_car_model_cb(self, mock_func):
        """ Test task used by scheduler to create car_model_get_picture tasksc"""
        self.prepopulate_db()
        self.assertEqual(task_car_model_cb(), 'SUCCESS')
        self.assertEqual(mock_func.call_count, 2)
        mock_func.assert_called_with(2)

    def test_create_number_plate(self):
        """ Test creation of number plate record with valid payload is successful""" 
        resp = self.client.post(PLATE_URL, self.payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp_car_model = resp.data.get('car_model')
        resp_car_model.pop('image')
        car_model = CarModel.objects.get(**resp_car_model)
        resp.data['car_model'] = car_model
        self.assertTrue(NumberPlate.objects.filter(**resp.data).exists())
        # without model field
        payload = {
            'number': 'ABC123',
            'owner': 'Peter',
            'car_model': {
                'manufacturer': 'volvo'
            }
        }
        resp = self.client.post(PLATE_URL, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # without manufacturer field 
        payload = {
            'number': 'ABC124',
            'owner': 'Peter',
            'car_model': {
                'model': '911'
            }
        }
        resp = self.client.post(PLATE_URL, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        number_plate = NumberPlate.objects.get(pk=resp.data['id'])
        car_model = CarModel.objects.get(manufacturer='', model='911')
        self.assertEqual(number_plate.car_model, car_model)

    def test_number_plates_duplicaton(self):
        """ Test creation of number plate that already exists, fails """
        self.prepopulate_db()
        resp = self.client.post(PLATE_URL, self.payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_number_plate(self):
        """ Test update of number plate record with valid payload, successful""" 
        resp = self.client.post(PLATE_URL, self.payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # update name
        payload = {
            'number': 'ANJ519',
            'owner': 'Jone'
        }
        url = reverse('numberplate-detail', kwargs={'pk': 1})
        resp = self.client.put(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        number_plate = NumberPlate.objects.get(pk=1)
        self.assertEqual(number_plate.owner, 'Jone')
        self.assertEqual(number_plate.car_model, None)
        # update with existing car model
        payload = {
            'number': 'ANJ519',
            'owner': 'Jone',
            'car_model': {
                'manufacturer': 'porsche',
                'model': '911'
            }
        }
        resp = self.client.put(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        number_plate = NumberPlate.objects.get(pk=1)
        car_model = CarModel.objects.get(manufacturer='porsche', model='911')
        self.assertEqual(number_plate.car_model, car_model)
        # update with existing manfacturer, but not combination of manufacturer and emty model
        payload = {
            'number': 'ANJ519',
            'owner': 'Jone',
            'car_model': {
                'manufacturer': 'porsche'
            }
        }
        resp = self.client.put(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        number_plate = NumberPlate.objects.get(pk=1)
        car_model = CarModel.objects.get(manufacturer='porsche', model='')
        self.assertEqual(number_plate.car_model, car_model)


    def test_number_plate_validation(self):
        """ Test creation of number plate format, fails"""
        # wrong number format
        payload = {
            'number': '12345',
            'owner': 'Peter'
        }
        resp = self.client.post(PLATE_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.dumps(resp.data), 
                        '{"number": ["Plate number should contain first three alphabetical letters '
                        'follewed by three numbers. exmp.: ABC123"]}')
        # owner field reuired 
        payload = {
            'number': 'ABC123'
        }
        resp = self.client.post(PLATE_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.dumps(resp.data), '{"owner": ["This field is required."]}')
