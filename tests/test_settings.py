#!/usr/bin/env python
# coding=utf-8
import pytest

from django_tree_perm import settings, SettingsProxy


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

    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "tests.settings_v2")
    assert SettingsProxy().DEBUG is False
    captured = capsys.readouterr()
    assert "Please set the correct" in captured.out
