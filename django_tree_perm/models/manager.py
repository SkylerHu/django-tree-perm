#!/usr/bin/env python
# coding=utf-8
from django.db import models

from django_tree_perm.utils import TREE_SPLIT_NODE_FLAG


class TreeNodeManager(models.Manager):
    pass


class TreeNodeQuerySet(models.QuerySet):
    def search_nodes(self, value):
        # 搜索值为空，搜索无结果
        queryset = self
        if not value:
            return queryset

        # 传的值是path路径
        if TREE_SPLIT_NODE_FLAG in value:
            qs = queryset.filter(path=value)
            if not qs.exists():
                qs = queryset.filter(path__startswith=value)
                if not qs.exists():
                    qs = queryset.filter(path__contains=value)
            return qs.limit_to_top_node()

        # 绝对叶子结点有值相等
        qs = queryset.filter(is_key=True, name=value)
        if qs.exists():
            return qs
        # 绝对叶子结点值有关联
        qs = queryset.filter(is_key=True, name__contains=value)
        if qs.exists():
            return qs

        # 根据name模糊搜索
        qs = queryset.filter(name__contains=value)
        return qs.limit_to_top_node()

    def limit_to_top_node(self):
        """若是按照路径查找，尽可能返回更少的结点。
        优先返回树结构上层的结点
        """
        qs = self
        first = qs.order_by("depth").first()
        if first:
            qs = qs.filter(depth__lte=first.depth)
        else:
            qs = qs.none()
        return qs

    def search_keys(self, value):
        queryset = self.filter(is_key=True)
        queryset = queryset.search_nodes(value=value)
        return queryset.order_by("name")

    def filter_by_perm(self, user_id, role_names=None, role_ids=None):
        queryset = self

        # 找出自己有权限的路径
        from django_tree_perm.models import NodeRole, PermRole

        nr_qs = NodeRole.objects.filter(user_id=user_id)
        if role_names:
            role_ids = list(PermRole.objects.filter(name__in=role_names).values_list("id", flat=True))
            if not role_ids:
                return queryset.none()
        if role_ids and len(role_ids) == 1:
            nr_qs = nr_qs.filter(role_id=role_ids[0])
        elif role_ids:
            nr_qs = nr_qs.filter(role_id__in=role_ids)
        paths = list(nr_qs.values("node__path").distinct())
        if not paths:
            return queryset.none()

        # 根据有权限的路径，其子结点也都有权限
        query = models.Q(path__in=paths)
        for path in paths:
            query = query | models.Q(path__startswith=f"{path}{TREE_SPLIT_NODE_FLAG}")
        queryset = queryset.filter(query)
        return queryset
