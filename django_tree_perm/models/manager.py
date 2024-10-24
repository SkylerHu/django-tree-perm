#!/usr/bin/env python
# coding=utf-8
import typing

from django.db import models

from django_tree_perm.utils import TREE_SPLIT_NODE_FLAG


class TreeNodeManager(models.Manager):
    """用于TreeNode objects管理"""

    pass


class TreeNodeQuerySet(models.QuerySet):
    """用于TreeNode扩展QuerySet查询方法"""

    def search_nodes(self, value: str) -> "TreeNodeQuerySet":
        """模糊搜索树结点，尽快少的返回结点数据

        - 若包含路径分隔符"."，则按照path搜索
            - 优先按照 path startswith搜索
            - 无结果继续 path contains查找
            - 最终返回结果，仅返回 树深度depth 最浅的结点
        - 按照 name 唯一标识搜索
            - 优先搜索 is_key=True, name=value的结点，若存在忽略深度depth直接返回
            - 若无继续搜索 is_key=True, name contains 的结点，若存在忽略深度depth直接返回
            - 其次搜索 name contains 的结点，最终返回结果，仅返回 树深度depth 最浅的结点

        Args:
            value: 搜索输入值

        Returns:
            TreeNodeQuerySet
        """
        # 搜索值为空，搜索无结果
        queryset = self
        if not value:
            return queryset.none()

        # 传的值是path路径
        if TREE_SPLIT_NODE_FLAG in value:
            qs = queryset.filter(path=value)
            if qs.exists():
                return qs
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

    def limit_to_top_node(self) -> "TreeNodeQuerySet":
        """若是按照路径查找，尽可能返回更少的结点。

        优先返回树结构中 深度depth 最浅的结点

        Returns:
            TreeNodeQuerySet
        """
        qs = self
        first = qs.order_by("depth").first()
        if first:
            qs = qs.filter(depth=first.depth)
        else:
            qs = qs.none()
        return qs

    def search_keys(self, value: str) -> "TreeNodeQuerySet":
        """仅搜索关键结点(key node)

        Args:
            value: 搜索输入值

        Returns:
            TreeNodeQuerySet
        """
        queryset = self.filter(is_key=True)
        qs = queryset.filter(name=value)
        if not qs.exists():
            # 绝对叶子结点值有关联
            qs = queryset.filter(name__contains=value)
        return qs.order_by("name")

    def filter_by_perm(self, user_id: int, roles: typing.Optional[typing.List[str]] = None) -> "TreeNodeQuerySet":
        """根据用户和角色搜索相关联的结点

        Args:
            user_id: 用户ID
            roles: 用户角色，有任意其中一个角色即可，不传递表示有任意角色即可.

        Returns:
            TreeNodeQuerySet
        """
        queryset = self

        # 找出自己有权限的路径
        from django_tree_perm.models import NodeRole

        nr_qs = NodeRole.objects.filter(user_id=user_id)
        if roles:
            nr_qs = nr_qs.filter(role__name__in=roles)
        paths = list(nr_qs.values_list("node__path", flat=True).distinct())
        if not paths:
            return queryset.none()

        # 根据有权限的路径，其子结点也都有权限
        query = models.Q(path__in=paths)
        for path in paths:
            query = query | models.Q(path__startswith=f"{path}{TREE_SPLIT_NODE_FLAG}")
        queryset = queryset.filter(query)
        return queryset
