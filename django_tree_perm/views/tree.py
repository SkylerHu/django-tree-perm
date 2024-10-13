#!/usr/bin/env python
# coding=utf-8
from http import HTTPStatus

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import login, authenticate

from django_tree_perm.models import User, TreeNode, PermRole, NodeRole
from django_tree_perm.models.utils import user_to_json
from django_tree_perm.utils import TREE_SPLIT_NODE_FLAG, get_tree_paths
from django_tree_perm.controller import TreeNodeManger

from .base import (
    BaseView,
    BaseListModelMixin,
    BaseCreateModelMixin,
    BaseRetrieveModelMixin,
    BaseUpdateModelMixin,
    BaseDestoryModelMixin,
)


def main_view(request):
    return render(request, "tree_perm/main.html")


class MetaView(BaseView):

    @classmethod
    def gen_user_data(cls, user, path=None):
        data = user_to_json(user)
        # 是否具备树和角色的管理权限
        data["tree_manager"] = user.is_superuser
        # 是否具备结点管理权限
        node_manager = False
        if path:
            paths = get_tree_paths(path)
            node_manager = NodeRole.objects.filter(
                user_id=user.id, role__can_manage=True, node__path__in=paths
            ).exists()
        data["node_manager"] = node_manager
        return data

    def get(self, request, *args, **kwargs):
        user = request.user

        if user and user.is_authenticated:
            path = request.GET.get("path", None)
            data = self.gen_user_data(user, path=path)
            return JsonResponse({"user": data}, status=HTTPStatus.OK)

        return JsonResponse({}, status=HTTPStatus.UNAUTHORIZED)

    def post(self, request, *args, **kwargs):
        """用户登录"""
        data = self.parese_request_body(request)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            data = self.gen_user_data(user)
            return JsonResponse({"user": data}, status=HTTPStatus.OK)
        return JsonResponse({"error": "用户名或者密码错误"}, status=HTTPStatus.BAD_REQUEST)


class TreeNodeView(BaseListModelMixin):

    model = TreeNode
    filter_fields = [
        "name",
        "disabled",
        "is_key",
        "parent_id",
        "parent__path",
        "path",
        "depth",
        "alias",
        "alias__icontains",
        "description",
        "description__icontains",
    ]
    ordering = ["path"]

    def filter_by_search(self, request, queryset):
        search = request.GET.get("search", None)
        user_id = request.GET.get("user_id", None)

        if user_id:
            # 找出用户有权限的结点
            queryset = queryset.filter_by_perm(user_id)

        if search:
            # 根据name模糊搜索
            queryset = queryset.search_nodes(search)

        return queryset

    def post(self, request, *args, **kwargs):
        data = self.parese_request_body(request)
        manager = TreeNodeManger.add_node(**data)
        return JsonResponse(manager.node.to_json(), status=HTTPStatus.CREATED)


class TreeNodeEditView(BaseRetrieveModelMixin):

    model = TreeNode
    pk_field = "path"

    def patch(self, request, *args, pk=None, **kwargs):
        node = self.get_object(pk)

        data = self.parese_request_body(request)
        manager = TreeNodeManger(node=node)
        manager.update_attrs(
            name=data.get("name"),
            alias=data.get("alias"),
            description=data.get("description"),
            parent_id=data.get("parent_id"),
        )
        return JsonResponse(manager.node.to_json(), status=HTTPStatus.CREATED)

    def delete(self, request, *args, pk=None, **kwargs):
        node = self.get_object(pk)

        data = node.to_json()
        manager = TreeNodeManger(node=node)
        manager.remove()
        return JsonResponse(data, status=HTTPStatus.NO_CONTENT)


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

        results = [node.to_json(partial=True) for node in queryset]
        return JsonResponse({"count": len(results), "results": results}, status=HTTPStatus.OK)


class TreeLoadView(BaseView):
    def get(self, request, *args, **kwargs):
        search = request.GET.get("search", None)
        path = request.GET.get("path", None)
        parent_path = request.GET.get("parent_path", None)
        depth = request.GET.get("depth", None)

        queryset = TreeNode.objects.filter(disabled=False)
        if depth:
            queryset = queryset.filter(depth__lte=depth)
        if path:
            queryset = queryset.filter(path=path)
        if parent_path:
            queryset = queryset.filter(path__startswith=f"{parent_path}{TREE_SPLIT_NODE_FLAG}")
        if search:
            queryset = queryset.search_nodes(search)

        count = queryset.count()
        trace_to_root = any([search, path, depth, parent_path])
        data = TreeNodeManger.to_json_tree(queryset, trace_to_root=trace_to_root)

        return JsonResponse({"count": count, "results": data}, status=HTTPStatus.OK)


class UserListView(BaseListModelMixin):

    model = User
    filter_fields = ["username", "is_active"]
    search_fields = ["username", "first_name", "last_name"]
    ordering = ["username"]


class UserDetailView(BaseRetrieveModelMixin):

    model = User
    pk_field = "username"


def get_node_form_request(request):
    node = None
    key_name = request.GET.get("key_name", None)
    node_id = request.GET.get("node_id", None)
    path = request.GET.get("path", None)
    node = TreeNodeManger.get_node_object(key_name=key_name, node_id=node_id, path=path)
    return node


class PermRoleView(BaseCreateModelMixin, BaseListModelMixin):

    model = PermRole
    filter_fields = ["name", "can_manage"]
    search_fields = ["name", "alias"]
    ordering = ["-can_manage", "id"]
    disabled_paginator = True

    def to_results(self, request, instances):
        node = get_node_form_request(request)
        results = [instance.to_json(path=node.path if node else None) for instance in instances]
        return results


class PermRoleEditView(BaseRetrieveModelMixin, BaseUpdateModelMixin, BaseDestoryModelMixin):

    model = PermRole
    pk_field = "name"

    def get(self, request, *args, pk=None, **kwargs):
        instance = self.get_object(pk)
        node = get_node_form_request(request)
        data = instance.to_json(path=node.path if node else None)
        return JsonResponse(data, status=HTTPStatus.OK)

    def delete(self, request, *args, pk=None, **kwargs):
        instance = self.get_object(pk)
        obj = instance.noderole_set.first()
        if obj:
            return JsonResponse(
                {
                    "error": f"角色存在关联的用户，例如结点：{obj.node.path} ，请先删除角色所有结点下的用户后再重试",
                },
                status=HTTPStatus.BAD_REQUEST,
            )
        data = self.model_to_json(request, instance)
        instance.delete()
        return JsonResponse(data, status=HTTPStatus.NO_CONTENT)


class NodeRoleView(BaseCreateModelMixin, BaseListModelMixin):

    model = NodeRole
    filter_fields = [
        "node_id",
        "node__name",
        "role_id",
        "role__name",
        "user_id",
        "user__username",
    ]
    search_fields = ["node__name"]

    def get_queryset(self, request, **kwargs):
        queryset = super().get_queryset(request, **kwargs)
        return queryset.select_related("node", "user", "role")

    def post(self, request, *args, **kwargs):
        data = self.parese_request_body(request)
        user_ids = data.pop("user_ids", None)
        objs = []
        if user_ids:
            for user_id in user_ids:
                instance = self.model(user_id=user_id, **data)
                instance.full_clean()
                objs.append(instance)
            instances = NodeRole.objects.bulk_create(objs, batch_size=1000)
            return JsonResponse(
                {
                    "count": len(instances),
                    "results": [self.model_to_json(request, instance) for instance in instances],
                },
                status=HTTPStatus.CREATED,
            )
        else:
            instance = self.model(**data)
            instance.full_clean()
            instance.save()
            return JsonResponse(self.model_to_json(request, instance), status=HTTPStatus.CREATED)


class NodeRoleEditView(BaseRetrieveModelMixin, BaseUpdateModelMixin, BaseDestoryModelMixin):

    model = NodeRole
    pk_field = "name"
