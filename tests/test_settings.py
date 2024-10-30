#!/usr/bin/env python
# coding=utf-8
import pytest

from django_tree_perm import settings, SettingsProxy
from django_tree_perm.models.utils import format_datetime_field
from django_tree_perm.models import Role


def test_settings():
    with pytest.raises(AttributeError):
        settings.DEBUG = True

    with pytest.raises(AttributeError):
        del settings.DEBUG


def test_proxy(monkeypatch, capsys):
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "tests.settings")
    assert SettingsProxy().DEBUG is False

    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "")
    assert SettingsProxy().DEBUG is False


@pytest.mark.django_db()
def test_zone(settings):
    settings.USE_TZ = True
    settings.TIME_ZONE = "Asia/Shanghai"

    role = Role.objects.create(name="test-role")
    value = format_datetime_field(role.created_at)
    assert value.endswith("UTC+0800")
