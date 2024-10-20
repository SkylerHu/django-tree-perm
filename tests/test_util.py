#!/usr/bin/env python
# coding=utf-8

from django_tree_perm import utils


def test_gen_paths():
    assert utils.get_tree_paths("") == []
    assert utils.get_tree_paths("a") == ["a"]
    assert utils.get_tree_paths("a.b.c") == ["a", "a.b", "a.b.c"]
    assert utils.get_tree_paths(["a.b.c", "a.b"]) == ["a", "a.b", "a.b.c"]


def test_parent_path():
    assert utils.get_path_parent("") == ""
    assert utils.get_path_parent("a") == ""
    assert utils.get_path_parent("a.b.c") == "a.b"
