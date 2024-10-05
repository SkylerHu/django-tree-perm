#!/usr/bin/env python
# coding=utf-8
import json
from http import HTTPStatus

from django.views import View
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render

from django_tree_perm import exceptions
from django_tree_perm.models import User, TreeNode
from django_tree_perm.controller import TreeNodeManger


def main_view(request):
    return render(request, "tree_perm/main.html")


class BaseView(View):

    @classmethod
    def parese_request_body(cls, request):
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST
        return data


class TreeNodeView(BaseView):

    def get(self, request, *args, **kwargs):
        search = request.GET.get("search", None)
        is_key = request.GET.get("is_key", None)
        user_id = request.GET.get("user_id", None)

        queryset = TreeNode.objects.filter(disabled=False)
        if is_key is not None:
            queryset = queryset.filter(is_key=bool(is_key))
        if user_id:
            user = get_object_or_404(User, pk=user_id)
            queryset = queryset.filter_by_perm(user.id)
        if search:
            queryset = queryset.search_nodes(search)

        # 分页返回
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 20))
        paginator = Paginator(queryset, page_size)
        results = [node.to_json() for node in paginator.get_page(page)]
        return JsonResponse({"count": len(results), "results": results}, status=HTTPStatus.OK)

    def post(self, request, *args, **kwargs):
        try:
            data = self.parese_request_body(request)
            manager = TreeNodeManger.add_node(**data)
        except (ValidationError, exceptions.ParamsValidateException) as e:
            return JsonResponse({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse(manager.node.to_json(), status=HTTPStatus.CREATED)


class TreeNodeEditView(BaseView):

    def patch(self, request, *args, **kwargs):
        pass

    def delete(self, request, *args, **kwargs):
        pass


class TreeLazyLoadView(BaseView):

    def get(self, request, *args, **kwargs):
        parent_id = request.GET.get("parent_id", None)
        parent_path = request.GET.get("parent_path", None)

        queryset = TreeNode.objects.filter(disabled=False)
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        elif parent_path:
            queryset = queryset.filter(parent__path=parent_path)
        else:
            # 若是不传递则返回根结点
            queryset = queryset.filter(depth=1)

        results = [node.to_json() for node in queryset]
        return JsonResponse({"count": len(results), "results": results}, status=HTTPStatus.OK)


class TreeLoadView(BaseView):
    def get(self, request, *args, **kwargs):
        search = request.GET.get("search", None)

        queryset = TreeNode.objects.filter(disabled=False)
