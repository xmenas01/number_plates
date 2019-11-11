import requests
import os
from celery import task
from celery.utils.log import get_task_logger
import xml.etree.ElementTree as ET

from django.conf import settings
from api.models import CarModel


logger = get_task_logger(__name__)


@task(bind=True, name='task.car_model.cb')
def task_car_model_cb(self):
    car_model_list = CarModel.objects.values_list('id', flat=True).filter(ctask_status='IN PROGRESS') 
    # import ipdb; ipdb.set_trace()
    if car_model_list:
        for car_model_id in car_model_list:
            task_car_model_get_picture.delay(car_model_id)
    return 'SUCCESS'
    
@task(bind=True, name='task.car_model_get_picture', time_limit=60)
def task_car_model_get_picture(self, car_model_id):
    car_model_values = CarModel.objects.values_list('manufacturer','model').get(pk=car_model_id)
    car_model_str = ' '.join(car_model_values).strip()
    logger.info(f'Runniong task towards car model: {car_model_str}')
    car_model = CarModel.objects.get(pk=car_model_id)
    try:
        image = get_image(car_model_str)
    except Exception as exc:
        err_msg = f'Failed to get image of car model {car_model_str}. Due to: {exc.__class__.__name__}:{exc}'
        logger.error(err_msg)
        car_model.ctask_status = 'FAILED'
        car_model.ctask_message = err_msg
        car_model.save()
        self.retry(exc=exc, countdown=20)
        return 'FAILED'
    car_model.image = image
    car_model.ctask_status = 'SUCCESS'
    car_model.ctask_message = ''
    car_model.save()
    return 'SUCCESS'


def get_image(car_model):
    IMAGE_PROVIDER_URL = 'https://www.carimagery.com/api.asmx'
    img_path = settings.MEDIA_ROOT+f'/images/{car_model}.jpg'
    if not os.path.exists(img_path):
        resp = requests.get(f'{IMAGE_PROVIDER_URL}/GetImageUrl?searchTerm={car_model}')
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
        img_url = root.text
        img_data = requests.get(img_url).content
        with open(img_path, 'wb') as handler:
            handler.write(img_data)
    return f'images/{car_model}.jpg'


