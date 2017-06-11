# Supervisord Overseer
Overseer is a user interface for monitoring of processes on multiple hosts.
It interacts with the xmlrpc API provided by Supervisord to display information and
control processes.

## Features
- Easy access to overview information such as number of running/not running processes.
- View process information on a per node or group level
- Stores actions so you know who did what and when

## Installation
- Download the source code
- Configure the application in one of the settings template files provided (located at supervisord_overseer/settings/<xxx>.py.template) and remove .template from the name
- To run locally execute: `python manage.py runserver`
- To run in docker
    - `docker-compose build`
    - First time starting the container, run `docker-compose up`, then use `docker-compose start/stop` to start/stop the container
- Create your first user by executing the command `python manage.py createsuperuser`