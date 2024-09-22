#!/usr/bin/env python
# coding=utf-8
from django.db import models

from django_tree_perm import utils
from django_tree_perm.utils import TREE_SPLIT_NODE_FLAG


class TreeNodeManager(models.Manager):

    def search_nodes(self, value=None):
        # 搜索值为空，搜索无结果
        queryset = self.filter(disabled=False)
        if value is None:
            return queryset
        # 传的值是path路径
        if TREE_SPLIT_NODE_FLAG in value:
            qs = queryset.filter(path__contains=value)
            return qs
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
        return qs

    def search_keys(self, value=None):
        queryset = self.filter(is_key=True, disabled=False)
        queryset = queryset.search_nodes(value=value)
        return queryset.order_by("name")

    def filter_by_perm(self, user_id, role_ids=None):
        queryset = self.filter(disabled=False)

        # 找出自己有权限的路径
        from django_tree_perm.models import NodeRole

        nr_qs = NodeRole.objects.filter(user_id=user_id, node__disabled=False)
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

    def to_json_tree(self):
        """转换成树形结构的数据
        尽量不要渲染整棵树，处理速度会很慢；
        可以在调用之前多使用filter函数
        """
        queryset = self
        if self.query.where:
            paths = utils.get_tree_paths(list(self.values_list("path", flat=True)))
            queryset = self.all().filter(path__in=paths)

        tree = []
        # 以parent_id为key, value是数组--存放直接子结点
        parent_child_nodes = {}
        for node in queryset:
            if node.parent_id:
                parent_child_nodes.setdefault(node.parent_id, [])
                parent_child_nodes[node.parent_id].append(node.to_json())
            else:
                tree.append(node.to_json())

        # 组装树形结构
        leafs = tree
        while True:
            if not leafs:
                break
            new_leafs = []
            for parent in leafs:
                children = parent_child_nodes.get(parent["id"], [])
                if children:
                    parent["children"] = children
                    new_leafs.extend(children)
            leafs = new_leafs

        return tree
