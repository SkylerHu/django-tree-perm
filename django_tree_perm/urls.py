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
                path("nodes/<str:pk>/", views.TreeNodeEditView.as_view()),
                path("load/", views.TreeLoadView.as_view()),
                path("lazyload/", views.TreeLazyLoadView.as_view()),
                path("perm/", views.PermView.as_view()),
                path("users/", views.UserListView.as_view()),
                path("users/<str:pk>/", views.UserDetailView.as_view()),
                path("roles/", views.RoleView.as_view()),
                path("roles/<str:pk>/", views.RoleEditView.as_view()),
                path("noderoles/", views.NodeRoleView.as_view()),
                path("noderoles/<str:pk>/", views.NodeRoleEditView.as_view()),
            ]
        ),
    ),
]
