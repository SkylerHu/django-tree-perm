#!/usr/bin/env python
# coding=utf-8
import datetime

from django_tree_perm import settings
from django.forms.models import model_to_dict


def format_dict_to_json(data):
    for k, v in data.items():
        if isinstance(v, (int, float, bool, str)):
            continue
        if isinstance(v, datetime.datetime):
            data[k] = v.strftime(settings.TREE_DATETIME_FORMAT)
        else:
            data[k] = str(v)


def user_to_json(user):
    """user对象转换成json数据"""
    data = model_to_dict(
        user,
        exclude=["groups", "user_permissions", "password", "last_login", "date_joined"],
    )
    format_dict_to_json(data)
    return data
