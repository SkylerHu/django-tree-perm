#!/usr/bin/env python
# coding=utf-8
from django.conf import settings as django_settings


__all__ = ["settings", "VERSION"]
__version__ = "1.0.2"

import typing

VERSION = __version__


class SettingsProxy(object):

    # 时间格式化
    TREE_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S UTC%z"

    def __getattribute__(self, attr: str) -> typing.Any:
        try:
            if hasattr(django_settings, attr):
                value = getattr(django_settings, attr)
            else:
                value = super(SettingsProxy, self).__getattribute__(attr)
        except AttributeError:
            raise AttributeError('settings has no attribute "{}"'.format(attr))
        return value

    def __setattr__(self, name: str, value: typing.Any) -> None:
        raise AttributeError("All properties of settings are not allowed to be changed.")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("All properties of settings are not allowed to be changed.")


settings = SettingsProxy()
