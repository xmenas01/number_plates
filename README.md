# Number plate assignment

Project pupose is to register user car number plates with car model into the system and get back car model image. For image retrieving, app uses https://www.carimagery.com/ site's REST API. 

This project uses [Django REST framework](chttps://www.django-rest-framework.org/) as API engine, [Celery](https://celery.com) for asynchronous jobs and [RabbitMQ](https://rabbitmq.com) as broker.

## Install

In order to skip tedious job of preparing enviroment, we can use docker-compose file.
```bash
# Spin-up containers
$ docker-compose up -d
# To stop containers
$ docker-compose down
# Get bash of app container
$ docker exec -it number_plates_app_1 /bin/bash
```

When enviroment is ready, we just need to create database tables and admin user. Do not forget admin password, which you provided for django. We will use it to connect into django admin panel.
```bash
# Create database tables and admin superuser 
$ python ./manage.py migrate
$ python ./manage.py createsuperuser --username admin --email admin@admin.com
```
We are done, enviroment is ready!!!

## Usage

Compose-file will spin-up three containers and two of them have admin GUI, you can visit them if you like:
* number_plates_app_1 (Django admin panel): http://localhost:8080/admin
* number_plates_broker_1 (RabbitMQ): http://localhost:15672/
* number_plates_worker_1 (Celery): bash only

*Default credentials: admin/admin*

App REST API can be tested using this link:
http://localhost:8080/api/plates/

App is covered by tests as well, in order to run them please use django unittest framework:
```bash
$ docker exec -it number_plates_app_1 /bin/bash
$ python ./manage.py test
```

### how it works?

User over REST API provides mondatary inputs like car number plate and owner name, these inputs is validated at moment of POST. Optionaly - car model info. All this payload data is saved into database. If car model is given, additional celery task is initiated to pull car model picture and save it. All added car number plates can be viewed over /api/plates/ endpoint.

payload example:
```json
{
    "number": "ANJ519",
    "owner": "Peter",
    "car_model": {
        "manufacturer": "porsche",
        "model": "911"
    }
}
```

Additional scheduled celery task is running as well for cases when car model is added over Django admin panel or in cases when for any reason instant image pull wasn't initiated.
