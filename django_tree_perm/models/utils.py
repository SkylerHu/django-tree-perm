#!/usr/bin/env python
# coding=utf-8
import datetime

from django.conf import settings
from django.forms.models import model_to_dict


def user_to_json(user):
    data = model_to_dict(
        user,
        exclude=["groups", "user_permissions", "password", "last_login", "date_joined"],
    )
    for k, v in data.items():
        if isinstance(v, (int, float, bool, str)):
            continue
        if isinstance(k, datetime.datetime):
            data[k] = v.strftime(settings.TREE_DATETIME_FORMAT)
        else:
            data[k] = str(v)
    return data
