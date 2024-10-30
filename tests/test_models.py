#!/usr/bin/env python
# coding=utf-8
import pytest
import json

from django.core.exceptions import ValidationError

from django_tree_perm.models import NodeRole, TreeNode, Role
from django_tree_perm.models.utils import user_to_json, format_dict_to_json
from django_tree_perm.models.tree import tree_validator
from django_tree_perm.models.manager import TreeNodeManager, TreeNodeQuerySet
from django_tree_perm.views.tree import RoleSerializer
from django_tree_perm.utils import TREE_SPLIT_NODE_FLAG


@pytest.mark.parametrize(
    "value,success",
    [
        ("root", True),
        ("root1", True),
        ("root-1_2", True),
        ("r", False),
        ("a.b", False),
        ("根结点", False),
        ("9root", False),
    ],
)
def test_name_validator(value, success):
    if success:
        tree_validator()(value)
    else:
        with pytest.raises(ValidationError):
            tree_validator()(value)


@pytest.mark.django_db()
def test_user_json(employee_user):
    keys = ["groups", "user_permissions", "password", "last_login", "date_joined"]
    data = user_to_json(employee_user)
    for key in keys:
        assert key not in data
    # 可序列化不报错
    json.dumps(data)

    data = employee_user.__dict__
    format_dict_to_json(data)
    json.dumps(data)


@pytest.mark.django_db()
def test_tree_node(dept_node):
    assert dept_node.path_prefix.endswith(TREE_SPLIT_NODE_FLAG)
    assert dept_node.depth == len(dept_node.path.split(TREE_SPLIT_NODE_FLAG))

    keys = ["id", "name", "alias", "parent_id", "is_key", "path"]
    data = dept_node.to_json(partial=True)
    assert sorted(data.keys()) == sorted(keys)

    other_keys = ["disabled", "description", "depth", "created_at", "updated_at"]
    data = dept_node.to_json()
    assert sorted(data.keys()) == sorted(keys + other_keys)


@pytest.mark.django_db()
def test_role_model(dev_role, employee_user, dept_node, key_node):
    keys = ["id", "name", "alias", "can_manage"]
    data = dev_role.to_json(partial=True)
    assert sorted(data.keys()) == sorted(keys)

    other_keys = ["description", "created_at", "updated_at"]
    data = dev_role.to_json()
    assert sorted(data.keys()) == sorted(keys + other_keys)

    data = dev_role.to_json(path=key_node.path)
    assert data["user_set"] == []

    # 角色关联用户
    NodeRole.objects.create(user=employee_user, node=dept_node, role=dev_role)
    NodeRole.objects.create(user=employee_user, node=key_node, role=dev_role)

    data = dev_role.to_json(path=key_node.path)
    user_set = data["user_set"]
    assert len(user_set) == 2
    # 按照最近排序顺序
    assert user_set[0]["node"]["id"] == key_node.id
    assert user_set[1]["node"]["id"] == dept_node.id


@pytest.mark.django_db()
def test_node_role_model(dev_role, employee_user, dept_node):
    node_role = NodeRole.objects.create(user=employee_user, node=dept_node, role=dev_role)

    keys = ["id", "node_id", "user_id", "role_id", "created_at"]
    data = node_role.to_json(partial=True)
    assert sorted(data.keys()) == sorted(keys)

    other_keys = ["role", "user", "node"]
    data = node_role.to_json()
    assert sorted(data.keys()) == sorted(keys + other_keys)
    for key in other_keys:
        assert isinstance(data[key], dict)


@pytest.mark.django_db()
def test_role_serialer(dev_role):
    s = RoleSerializer(dev_role)
    assert "user_set" not in s.data


@pytest.mark.django_db()
def test_node_manager(root_node, dept_node, key_node):
    assert isinstance(TreeNode.objects, TreeNodeManager)
    queryset = TreeNode.objects.all()
    assert isinstance(queryset, TreeNodeQuerySet)

    # 空值无结果
    qs = queryset.search_nodes("")
    assert qs.count() == 0
    # 按照根目录搜索，返回最少的结果
    qs = queryset.search_nodes(root_node.name)
    assert qs.count() == 1

    # 优先按照path准确搜索返回
    qs = queryset.search_nodes(dept_node.path)
    assert qs.count() == 1
    assert qs.first().id == dept_node.id
    # path__startswith
    qs = queryset.search_nodes(dept_node.path[:-1])
    assert qs.count() == 2
    # path__contains
    qs = queryset.search_nodes("dept1.prod")
    assert qs.count() == 6
    # is_key and name ==
    qs = queryset.search_nodes(key_node.name)
    assert qs.count() == 1
    assert qs.first().id == key_node.id
    # is_key and name__startswith
    qs = queryset.search_nodes(key_node.name[:-1])
    assert qs.count() == 3
    # name__contains
    qs = queryset.search_nodes("dept")
    assert qs.count() == 2
    # 无结果
    qs = queryset.search_nodes("dept3")
    assert qs.count() == 0

    # 测试search_keys
    qs = queryset.search_keys(key_node.name)
    assert qs.count() == 1
    assert qs.first().id == key_node.id
    qs = queryset.search_keys(dept_node.path)
    assert qs.count() == 0


@pytest.mark.django_db()
def test_node_filter_perm(dept_node, employee_user, dev_role):
    queryset = TreeNode.objects.all()
    assert isinstance(queryset, TreeNodeQuerySet)

    qs = queryset.filter_by_perm(user_id=employee_user.id)
    assert qs.count() == 0

    NodeRole.objects.create(user=employee_user, node=dept_node, role=dev_role)
    qs = queryset.filter_by_perm(user_id=employee_user.id)
    assert qs.count() == 13
    # 角色不存在
    assert not Role.objects.filter(name="test").exists()
    qs = queryset.filter_by_perm(user_id=employee_user.id, roles=["test"])
    assert qs.count() == 0
