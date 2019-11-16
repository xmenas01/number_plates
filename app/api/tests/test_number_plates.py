from unittest.mock import patch
import json

from django.test import TestCase
from rest_framework.reverse import reverse

from rest_framework.test import APIClient
from rest_framework import status
from api.models import NumberPlate, CarModel
from api.tasks import task_car_model_cb, task_car_model_get_picture


PLATE_URL = reverse('numberplate-list')
PLATE_URL_DETAIL = reverse('numberplate-detail', kwargs={'pk': 1})

class NumberPlateTest(TestCase):
    """ Test the number plate API """
    def setUp(self):
        self.client = APIClient()
        self.payload = {
            'number': 'EZJ123',
            'owner': 'TOM',
            'car_model': {
                'manufacturer': 'vw',
                'model': 'Golf'
            }
        }
        self.prepopulate_db()

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
        mock_get_image.side_effect = Exception('shit happens') 
        # funcion retunrs FAILED
        self.assertEqual(task_car_model_get_picture(car_model_id=1), 'FAILED')
        mock_get_image.assert_called_with('porsche 911')
        car_model = CarModel.objects.get(pk=1)
        #  CarModel DB have saved proper values
        self.assertEqual(car_model.ctask_status, 'FAILED')
        self.assertEqual(car_model.ctask_message, 'Failed to get image of car model porsche 911. Due to: Exception:shit happens')

    @patch('api.tasks.get_image')
    def test_task_car_model_get_picture_success(self, mock_get_image):
        mock_get_image.return_value = 'images/porsche 911.jpg'
        self.assertEqual(task_car_model_get_picture(car_model_id=1), 'SUCCESS')
        mock_get_image.assert_called_with('porsche 911')
        car_model = CarModel.objects.get(pk=1)
        #  CarModel DB have saved proper values
        self.assertEqual(car_model.image, 'images/porsche 911.jpg')
        self.assertEqual(car_model.ctask_status, 'SUCCESS')

    @patch('api.tasks.task_car_model_get_picture.delay')
    def test_task_car_model_cb_success(self, mock_func):
        """ Test task used by scheduler to create car_model_get_picture tasksc"""
        self.assertEqual(task_car_model_cb(), 'SUCCESS')
        self.assertEqual(mock_func.call_count, 2)
        mock_func.assert_called_with(2)

    def test_create_number_plate_success(self):
        """ Test creation of number plate record with valid payload is successful""" 
        resp = self.client.post(PLATE_URL, self.payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp_car_model = resp.data.get('car_model')
        resp_car_model.pop('image')
        car_model = CarModel.objects.get(**resp_car_model)
        resp.data['car_model'] = car_model
        self.assertTrue(NumberPlate.objects.filter(**resp.data).exists())

    def test_create_number_plate_without_car_model(self):
        """ Test creation of number plate record without car_model is successful""" 
        payload = {
            'number': 'abc123',
            'owner': 'Peter'
        }
        resp = self.client.post(PLATE_URL, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        number_plate = NumberPlate.objects.get(pk=resp.data['id'])
        self.assertEqual(number_plate.number, 'ABC123')

    def test_create_number_plate_without_car_model_model(self):
        """ Test creation of number plate record without car_model model is successful""" 
        payload = {
            'number': 'ABC123',
            'owner': 'Peter',
            'car_model': {
                'manufacturer': 'volvo'
            }
        }
        resp = self.client.post(PLATE_URL, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        number_plate = NumberPlate.objects.get(pk=resp.data['id'])
        car_model = CarModel.objects.get(manufacturer='volvo', model='')
        self.assertEqual(number_plate.car_model, car_model)

    def test_create_number_plate_without_car_model_manufacturer(self):
        """ Test creation of number plate record without car_model manufacturer is successful""" 
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

    def test_create_number_plate_owner_missing(self):
        """ Test create of number plate record owner missing""" 
        payload = {
            'number': 'ANJ520'
        }
        resp = self.client.post(PLATE_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.dumps(resp.data), '{"owner": ["This field is required."]}')

    def test_create_number_plate_put_method_on_create_endpoint(self):
        """ Test creation enpoint, try to use put method""" 
        # not allowed method
        resp = self.client.put(PLATE_URL, self.payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_number_plates_duplicaton(self):
        """ Test creation of number plate that already exists, fails """
        resp = self.client.post(PLATE_URL, self.payload, format='json')
        resp = self.client.post(PLATE_URL, self.payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_number_plate_owner_with_emty_car_model(self):
        """ Test update of number plate owner""" 
        payload = {
            'number': 'ANJ519',
            'owner': 'Jone'
        }
        resp = self.client.put(PLATE_URL_DETAIL, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        number_plate = NumberPlate.objects.get(pk=1)
        self.assertEqual(number_plate.owner, 'Jone')
        self.assertEqual(number_plate.car_model, None)

    def test_update_number_plate_car_model(self):
        """ Test update of number plate owner""" 
        # update with existing car model
        payload = {
            'number': 'ANJ519',
            'owner': 'Peter',
            'car_model': {
                'manufacturer': 'vw',
                'model': 'Passat'
            }
        }
        resp = self.client.put(PLATE_URL_DETAIL, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        number_plate = NumberPlate.objects.get(pk=1)
        car_model = CarModel.objects.get(manufacturer='vw', model='passat')
        self.assertEqual(number_plate.car_model, car_model)

    def test_update_number_plate_car_model_with_existing_car_model(self):
        resp = self.client.post(PLATE_URL, self.payload, format='json')
        payload = {
            'number': 'ANJ519',
            'owner': 'Peter',
            'car_model': {
                'manufacturer': 'vw',
                'model': 'Golf'
            }
        }
        resp = self.client.put(PLATE_URL_DETAIL, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        number_plate = NumberPlate.objects.get(pk=1)
        car_model = CarModel.objects.get(manufacturer='vw', model='golf')
        self.assertEqual(number_plate.car_model, car_model)

    def test_update_number_plate_car_model_by_removing_model(self):
        payload = {
            'number': 'ANJ519',
            'owner': 'Jone',
            'car_model': {
                'manufacturer': 'porsche'
            }
        }
        resp = self.client.put(PLATE_URL_DETAIL, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        number_plate = NumberPlate.objects.get(pk=1)
        car_model = CarModel.objects.get(manufacturer='porsche', model='')
        self.assertEqual(number_plate.car_model, car_model)

    def test_update_number_plate_with_missing_owner(self):
        payload = {
            'number': 'ANJ519'
        }
        resp = self.client.put(PLATE_URL_DETAIL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.dumps(resp.data), '{"owner": ["This field is required."]}')

    def test_detail_endpint_with_post_method(self):
        resp = self.client.post(PLATE_URL_DETAIL, self.payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_number_plate_format(self):
        """ Test creation of number plate format, failed"""
        # wrong number format
        number_list = ['1ab123', 'ab2abe', 'aabcde', 'ab123c', '12345']
        for number in number_list:
            payload = {
                'number': number,
                'owner': 'Peter'
            }
            resp = self.client.post(PLATE_URL, payload)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(json.dumps(resp.data), 
                            '{"number": ["Plate number should contain first three alphabetical letters '
                            'follewed by three numbers. exmp.: ABC123"]}')

    def test_number_plate_length(self):
        """ Test creation of number plate length, failed"""
        payload = {
            'number': '1bc123g',
            'owner': 'Peter'
        }
        resp = self.client.post(PLATE_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('. '.join(resp.data['number']),
                        'Plate number should contain first three alphabetical letters follewed by three numbers. exmp.: ABC123. '
                        'Ensure this field has no more than 6 characters.')
