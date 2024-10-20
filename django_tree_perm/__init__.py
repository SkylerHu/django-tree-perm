#!/usr/bin/env python
# coding=utf-8
import os
import traceback
import importlib


__all__ = ["settings", "VERSION"]
__version__ = "0.1.0"

import typing

VERSION = __version__

_BLACK_ATTRS = ["_settings", "__dict__"]


class SettingsProxy(object):

    def __init__(self) -> None:
        _settings = None
        # 兼容在Django项目中的使用
        _settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
        try:
            if _settings_module:
                _settings = importlib.import_module(_settings_module)
            else:
                print(
                    "Warning: settings configuration file not found, Can be set through the environment variable "
                    '"export PY_SETTINGS_MODULE=${your_project.settings_file.py}"'
                )
        except Exception:
            traceback.print_exc()
            print('Please set the correct "PY_SETTINGS_MODULE".')

        self._settings = _settings

    # 是否调试模式
    DEBUG = False

    TREE_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __getattribute__(self, attr: str) -> typing.Any:
        try:
            if attr in _BLACK_ATTRS:
                # 白名单，内置属性直接返回
                return super(SettingsProxy, self).__getattribute__(attr)

            if self._settings is not None and hasattr(self._settings, attr):
                value = getattr(self._settings, attr)
            else:
                value = super(SettingsProxy, self).__getattribute__(attr)
        except AttributeError:
            raise AttributeError('settings has no attribute "{}"'.format(attr))
        return value

    def __setattr__(self, name: str, value: typing.Any) -> None:
        if name in _BLACK_ATTRS and not hasattr(self, name):
            return super(SettingsProxy, self).__setattr__(name, value)
        raise AttributeError("All properties of settings are not allowed to be changed.")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("All properties of settings are not allowed to be changed.")


settings = SettingsProxy()
