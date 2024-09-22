#!/usr/bin/env python
# coding=utf-8
import re

from django.db import transaction, models
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from django_tree_perm import exceptions
from django_tree_perm.models import TreeNode, NodeRole


class TreeHelper(object):

    def __init__(self, **kwargs):
        self.node = get_object_or_404(TreeNode, **kwargs)

    @classmethod
    def find_parent_node(cls, parent=None, parent_id=None, parent_path=None, required=False):
        try:
            if not parent and parent_id:
                parent = TreeNode.objects.get(id=parent_id)
            if not parent and parent_path:
                parent = TreeNode.objects.get(path=parent_path)
        except ObjectDoesNotExist:
            pass

        if parent:
            if parent.is_key:
                raise exceptions.ParamsValidateException("This key node is not allowed to be a parent node.")
            if parent.disabled:
                raise exceptions.ParamsValidateException("This node is disabled.")
        elif required:
            raise exceptions.ParamsValidateException("Parent node not found, and cannot be null.")
        return parent

    @classmethod
    def add_node(cls, name, alias="", description="", parent=None, parent_id=None, parent_path=None, is_key=False):
        parent = cls.find_parent_node(parent=parent, parent_id=parent_id, parent_path=parent_path)
        if is_key and not parent:
            # 叶子结点不允许是根结点
            raise exceptions.ParamsValidateException("Leaf nodes are not allowed to be root node.")
        values = {
            "name": name,
            "alias": alias,
            "description": description,
            "parent": parent,
            "is_key": is_key,
            "disabled": False,
        }
        node = TreeNode(**values)
        node.save()
        return cls(node)

    def update_attrs(self, name=None, alias=None, description=None):
        node = self.node
        is_change = False
        if name and node.name != name:
            is_change = True
            node.name = name
        if alias is not alias and node.alias != alias:
            is_change = True
            node.alias = alias
        if description is not None and node.description != description:
            is_change = True
            node.description = description
        if is_change:
            node.save()

    @transaction.atomic
    def move_path(self, parent=None, parent_id=None, parent_path=None):
        parent = self.find_parent_node(parent=parent, parent_id=parent_id, parent_path=parent_path, required=True)
        node = self.node
        if node.id == parent.id:
            # 不能选择自己
            raise exceptions.ParamsValidateException("Cannot be its own child node.")
        if node.parent_id == parent.id:
            # 已在节点下无需处理
            return 0

        node.parent = parent
        # 要更新所有子结点path属性
        old_prefix = node.path_prefix  # 提前记录旧的树路径
        nodes = list(TreeNode.objects.filter(path__startswith=old_prefix))
        if nodes:
            node._patch_attrs()
            new_prefix = node.path_prefix
            for _node in nodes:
                re_prefix = old_prefix.replace(".", "\\.")
                _node.path = re.sub(rf"^{re_prefix}", new_prefix, _node.path, flags=0)
                _node._patch_attrs()
            nodes.append(node)
            rows = TreeNode.objects.bulk_update(nodes, TreeNode.TREE_SPECIAL_FIELDS, batch_size=1000)
        else:
            node.save()
            rows = 1
        return rows

    @transaction.atomic
    def remove(self, clear_chidren=False):
        node = self.node
        if node.disabled:
            return 0
        if node.is_key:
            node.parent = None
            node.disabled = True
            node.save()
            # 清除结点相关用户权限
            NodeRole.objects.filter(node_id=node.id).delete()
            return 0

        has_children = node.children.exists()
        if has_children and not clear_chidren:
            raise exceptions.ParamsValidateException("Deleted nodes cannot be selected.")

        if not has_children:
            # 会级联删除相关用户权限
            node.delete()
            return 1
        # 处理子结点
        query_set = TreeNode.objects.filter(models.Q(id=node.id) | models.Q(path__startswith=node.path_prefix))
        # 更新所有叶子结点为disabled
        node_ids = []
        nodes = []
        for _node in query_set.filter(is_key=True, disabled=False):
            _node.disabled = True
            _node.parent = None
            _node._patch_attrs()
            nodes.append(_node)
            node_ids.append(_node.id)
        if nodes:
            TreeNode.objects.bulk_update(nodes, TreeNode.TREE_SPECIAL_FIELDS, batch_size=1000)
            # 清除结点相关用户权限
            NodeRole.objects.filter(node_id__in=node_ids).delete()
        # 删除所有子结点
        row, _ = query_set.filter(is_key=False).delete()
        return row

    @classmethod
    def enable_key_node(cls, name, parent=None, parent_id=None, parent_path=None):
        node = TreeNode.objects.get(name=name, is_key=True)
        if not node.disabled:
            raise exceptions.ParamsValidateException("The node is not disabled.")

        parent = cls.find_parent_node(parent=parent, parent_id=parent_id, parent_path=parent_path, required=True)

        node.disabled = False
        node.parent = parent
        node.save()

        return cls(node)


class PermHelper(object):

    def __init__(self, user):
        self.user = user

    def has_perm(self, node):
        pass
