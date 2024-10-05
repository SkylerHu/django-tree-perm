#!/usr/bin/env python
# coding=utf-8

from django.urls import path, include

from django_tree_perm import views


urlpatterns = [
    path("", views.main_view),
    path(
        "tree/",
        include(
            [
                path("nodes/", views.TreeNodeView.as_view()),
                path("nodes/lazyload/", views.TreeLazyLoadView.as_view()),
            ]
        ),
    ),
]
