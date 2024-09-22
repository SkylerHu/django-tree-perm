#!/usr/bin/env python
# coding=utf-8
from django.views import View

from django.http import HttpResponse

from django_tree_perm import utils
from django_tree_perm.models import TreeNode


class TreeNodeView(View):

    def get(self, request, *args, **kwargs):
        path = request.GET.get("path", None)
        return HttpResponse("Hello, World!")
