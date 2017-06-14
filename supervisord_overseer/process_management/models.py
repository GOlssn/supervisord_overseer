# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import OperationalError, connection
from django.db import models


# Create your models here.


class SystemEventViewTransformer():
    def __init__(self, query_set):
        self.query_set = query_set

    @property
    def list(self):
        _lst = []
        for element in self.query_set:
            transformed = {
                'username': element.user.username,
                'created': element.created.strftime('%Y-%m-%d %H:%M'),
                'description': element.description
            }

            # if hasattr(element, 'deployevent'):
            #     transformed['description'] = "{} {}".format(element.description, element.deployevent.something)

            _lst.append(transformed)

        return _lst


class SystemEvent(models.Model):
    user = models.ForeignKey(User, help_text="The user who performed the action")
    created = models.DateTimeField(auto_now=True, auto_created=True, help_text="The time when the event was happening")
    description = models.CharField(max_length=256, default='')

    @staticmethod
    def restarted_process(user, process: str, node: str):
        try:
            SystemEvent(user=user, description='{} was restarted on {}'.format(process, node)).save()
        except OperationalError:
            connection.close()

    @staticmethod
    def stopped_process(user, process: str, node: str):
        try:
            SystemEvent(user=user, description='{} was stopped on {}'.format(process, node)).save()
        except OperationalError:
            connection.close()

    @staticmethod
    def free_text(user, description: str):
        try:
            SystemEvent(user=user, description=description).save()
        except OperationalError:
            connection.close()