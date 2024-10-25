#!/usr/bin/env python
# coding=utf-8
import typing
from http import HTTPStatus

from django.db import models
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth import login, authenticate

from django_tree_perm.models import User, TreeNode, Role, NodeRole
from django_tree_perm.models.utils import user_to_json
from django_tree_perm.controller import TreeNodeManger, PermManager
from django_tree_perm import exceptions

from .base import (
    BaseView,
    BasePermissionView,
    BaseModelSerializer,
    BaseListModelMixin,
    BaseCreateModelMixin,
    BaseRetrieveModelMixin,
    BaseUpdateModelMixin,
    BaseDestoryModelMixin,
)


def main_view(request: HttpRequest) -> HttpResponse:
    """
    前端管理页面的入口
    """
    return render(request, "tree_perm/main.html")


class PermView(BaseView):

    @classmethod
    def gen_user_data(cls, request: HttpRequest, user: User) -> dict:
        path = request.GET.get("path", None)
        key_name = request.GET.get("key_name", None)
        roles = request.GET.get("roles", None)
        if roles:
            roles = roles.split(",")

        data = user_to_json(user)
        # 是否具备树和角色的管理权限
        data["tree_manager"] = PermManager.has_tree_perm(user)
        # 是否具备结点管理权限
        data["node_manager"] = PermManager.has_node_perm(user, path=path, key_name=key_name, can_manage=True)
        # 是否有该结点角色权限
        data["node_perm"] = PermManager.has_node_perm(user, path=path, key_name=key_name, roles=roles)
        return data

    def get(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> JsonResponse:
        user = request.user
        if not user or not user.is_authenticated:
            return JsonResponse({"error": "Please log in."}, status=HTTPStatus.UNAUTHORIZED)

        data = self.gen_user_data(request, user)
        return JsonResponse({"user": data}, status=HTTPStatus.OK)

    def post(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> JsonResponse:
        """用户登录"""
        data = self.parese_request_body(request)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            data = self.gen_user_data(request, user)
            return JsonResponse({"user": data}, status=HTTPStatus.OK)
        return JsonResponse({"error": "Wrong username or password."}, status=HTTPStatus.BAD_REQUEST)


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
        "description__icontains",
    ]
    ordering = ["path"]

    def filter_by_search(self, request: HttpRequest, queryset: models.QuerySet) -> models.QuerySet:
        search = request.GET.get("search", None)
        user_id = request.GET.get("user_id", None)

        if user_id:
            # 找出用户有权限的结点
            queryset = queryset.filter_by_perm(user_id)

        if search:
            # 根据name模糊搜索
            queryset = queryset.search_nodes(search)

        return queryset

    def post(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> JsonResponse:
        data = self.parese_request_body(request)
        manager = TreeNodeManger.add_node(
            name=data.get("name"),
            alias=data.get("alias") or "",
            description=data.get("description") or "",
            parent_id=data.get("parent_id"),
            parent_path=data.get("parent_path"),
            is_key=bool(data.get("is_key", False)),
            user=request.user,
        )
        return JsonResponse(manager.node.to_json(), status=HTTPStatus.CREATED)


class TreeNodeEditView(BaseRetrieveModelMixin):

    model = TreeNode
    pk_field = "path"

    def patch(
        self,
        request: HttpRequest,
        *args: typing.Any,
        pk: typing.Optional[str] = None,
        **kwargs: typing.Any,
    ) -> JsonResponse:
        node = self.get_object(pk)

        data = self.parese_request_body(request)
        manager = TreeNodeManger(node=node, user=request.user)
        manager.update_attrs(
            name=data.get("name"),
            alias=data.get("alias"),
            description=data.get("description"),
            parent_id=data.get("parent_id"),
            parent_path=data.get("parent_path"),
        )
        return JsonResponse(manager.node.to_json(), status=HTTPStatus.OK)

    def delete(
        self,
        request: HttpRequest,
        *args: typing.Any,
        pk: typing.Optional[str] = None,
        **kwargs: typing.Any,
    ) -> JsonResponse:
        node = self.get_object(pk)

        data = node.to_json()
        manager = TreeNodeManger(node=node, user=request.user)
        manager.remove()
        return JsonResponse(data, status=HTTPStatus.NO_CONTENT)


class TreeLazyLoadView(BasePermissionView):

    def get(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> JsonResponse:
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

        count = queryset.count()
        results = [node.to_json(partial=True) for node in queryset]
        return JsonResponse({"count": count, "results": results}, status=HTTPStatus.OK)


class TreeLoadView(BasePermissionView):
    def get(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> JsonResponse:
        search = request.GET.get("search", None)
        path = request.GET.get("path", None)
        depth = request.GET.get("depth", None)

        queryset = TreeNode.objects.filter(disabled=False)
        if depth:
            queryset = queryset.filter(depth__lte=depth)
        if path:
            queryset = queryset.filter(path=path)
        if search:
            queryset = queryset.search_nodes(search)

        count = queryset.count()
        trace_to_root = any([search, path, depth])
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


class RoleSerializer(BaseModelSerializer):

    def __init__(self, instance: Role, many: bool = False, context: typing.Optional[dict] = None) -> None:
        super().__init__(instance, many, context)
        request = self.context.get("request")
        if request:
            node = TreeNodeManger.get_node_object(**request.GET.dict())
            self.context["node"] = node

    def to_representation(self, instance: Role) -> dict:
        node = self.context.get("node")
        data = instance.to_json(path=node.path if node else None)
        return data


class RoleView(BaseCreateModelMixin, BaseListModelMixin):

    model = Role
    filter_fields = ["name", "can_manage"]
    search_fields = ["name", "alias"]
    ordering = ["-can_manage", "id"]
    disabled_paginator = True
    serializer_class = RoleSerializer

    def check_create_permission(self, request: HttpRequest, **kwargs: typing.Any) -> None:
        if not PermManager.has_tree_perm(request.user):
            raise exceptions.PermDenyException("Only superuser is allowed to add new role.")


class RoleEditView(BaseRetrieveModelMixin, BaseUpdateModelMixin, BaseDestoryModelMixin):

    model = Role
    pk_field = "name"
    serializer_class = RoleSerializer

    def check_object_permissions(
        self, request: HttpRequest, obj: Role, data: typing.Optional[dict] = None, **kwargs: typing.Any
    ) -> None:
        if not PermManager.has_tree_perm(request.user):
            raise exceptions.PermDenyException("Only superuser is allowed to operate roles.")

        if request.method != "PATCH":
            return

        name = data.get("name", None) if data else None
        if name and obj.name != name:
            raise exceptions.ParamsValidateException("The role name is used for permission, cannot be modified.")

    def delete(
        self,
        request: HttpRequest,
        *args: typing.Any,
        pk: typing.Optional[str] = None,
        **kwargs: typing.Any,
    ) -> JsonResponse:
        instance = self.get_object(pk)
        obj = instance.noderole_set.first()
        if obj:
            return JsonResponse(
                {
                    "error": f"角色存在关联的用户，例如结点：{obj.node.path} ，请先删除角色所有结点下的用户后再重试",
                },
                status=HTTPStatus.BAD_REQUEST,
            )
        return super().delete(request, *args, pk=pk, **kwargs)


class NodeRoleView(BaseCreateModelMixin, BaseListModelMixin):

    model = NodeRole
    filter_fields = [
        "node_id",
        "node__path",
        "node__path__in",
        "role_id",
        "role__name",
        "role__name__in",
        "user_id",
        "user__username",
        "user__username__in",
    ]
    search_fields = ["node__path"]

    def get_queryset(self, request: HttpRequest, **kwargs: typing.Any) -> models.QuerySet:
        queryset = super().get_queryset(request, **kwargs)
        return queryset.select_related("node", "user", "role")

    def filter_queryset(self, request: HttpRequest, **kwargs: typing.Any) -> models.QuerySet:
        queryset = super().filter_queryset(request, **kwargs)
        key_names = request.GET.get("key_names", None)
        if key_names:
            queryset = queryset.filter(node__is_key=True, node__name__in=key_names.split(","))
        return queryset

    def check_create_permission(
        self, request: HttpRequest, data: typing.Optional[dict] = None, **kwargs: typing.Any
    ) -> None:
        node = TreeNodeManger.get_node_object(required=True, **(data or {}))
        if node and not PermManager.has_node_perm(request.user, path=node.path, can_manage=True):
            raise exceptions.PermDenyException(f"No permission to manage role members for the path={node.path}")

    def post(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> JsonResponse:
        data = self.parese_request_body(request)
        self.check_create_permission(request, data=data)

        node = TreeNodeManger.get_node_object(required=True, **data)

        role_id = data.get("role_id", "")
        role_name = data.get("role_name", "")
        try:
            if role_name:
                role = Role.objects.get(name=role_name)
            else:
                role = Role.objects.get(id=role_id)
        except Exception as e:
            raise exceptions.ParamsValidateException(f"role_id={role_id} or role_name={role_name} not exists {e}")

        user_ids = data.pop("user_ids", None)
        if request.content_type == "multipart/form-data":
            user_ids = request.POST.getlist("user_ids")

        if user_ids:
            instances = []
            for user_id in user_ids:
                obj, created = NodeRole.objects.get_or_create(user_id=user_id, node=node, role=role)
                if created:
                    instances.append(obj)
            serializer = self.serializer_class(instances, many=True, context={"request": request})
            return JsonResponse(
                {
                    "count": len(instances),
                    "results": serializer.data,
                },
                status=HTTPStatus.CREATED,
            )
        else:
            instance = NodeRole(user_id=data.get("user_id"), node=node, role=role)
            instance.full_clean()
            instance.save()
            serializer = self.serializer_class(instance, context={"request": request})
            return JsonResponse(serializer.data, status=HTTPStatus.CREATED)


class NodeRoleEditView(BaseRetrieveModelMixin, BaseDestoryModelMixin):

    model = NodeRole
    pk_field = "name"

    def check_object_permissions(self, request: HttpRequest, obj: NodeRole, **kwargs: typing.Any) -> None:
        node = obj.node
        if not PermManager.has_node_perm(request.user, path=node.path, can_manage=True):
            raise exceptions.PermDenyException(f"No permission to manage role members for the path={node.path}")
