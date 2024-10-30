#!/usr/bin/env python
# coding=utf-8
import datetime

from django_tree_perm import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.forms.models import model_to_dict

from django.contrib.auth import get_user_model


User = get_user_model()


def format_datetime_field(time_field: models.DateTimeField) -> str:
    if settings.USE_TZ:
        aware_datetime = time_field
    else:
        aware_datetime = timezone.make_aware(time_field)
    local_datetime = timezone.localtime(aware_datetime)
    return local_datetime.strftime(settings.TREE_DATETIME_FORMAT)


def format_dict_to_json(data: dict) -> None:
    for k, v in data.items():
        if isinstance(v, (int, float, bool, str)):
            continue
        if isinstance(v, datetime.datetime):
            data[k] = format_datetime_field(v)
        else:
            data[k] = str(v)


def user_to_json(user: AbstractUser) -> dict:
    """user对象转换成json数据"""
    data = model_to_dict(
        user,
        exclude=["groups", "user_permissions", "password", "last_login", "date_joined"],
    )
    format_dict_to_json(data)
    return data
