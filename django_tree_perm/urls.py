#!/usr/bin/env python
# coding=utf-8

from django.urls import path, re_path, include

from django_tree_perm import views


urlpatterns = [
    path(
        "tree/",
        include(
            [
                path("", views.TreeNodeView.as_view()),
            ]
        ),
        namespace="django_tree_perm",
    ),
]
