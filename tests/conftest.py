#!/usr/bin/env python
# coding=utf-8
import pytest
import json

from django_tree_perm.controller import TreeNodeManger
from django_tree_perm.models import TreeNode, Role


@pytest.fixture
def init_tree():
    """初始化树结构"""
    with open("tests/fixtures/tree.json", "rb") as f:
        content = f.read()
    data = json.loads(content)
    TreeNodeManger.load_tree_data(data)


@pytest.fixture
def root_node(init_tree):
    node = TreeNode.objects.get(path="com")
    assert node.depth == 1
    return node


@pytest.fixture
def dept_path():
    return "com.dept1"


@pytest.fixture
def dept_node(init_tree, dept_path):
    node = TreeNode.objects.get(path=dept_path)
    # 有子节点
    assert TreeNode.objects.filter(parent_id=node.id).exists()
    return node


@pytest.fixture
def key_path(dept_path):
    path = "com.dept1.product2.system1.appkey1"
    assert path.startswith(dept_path)
    return path


@pytest.fixture
def key_node(init_tree, key_path, dept_node):
    """关键结点，且是dept_node的孙子结点"""
    node = TreeNode.objects.get(path=key_path, is_key=True)
    assert node.path.startswith(dept_node.path_prefix)
    return node


@pytest.fixture
def no_child_node(init_tree):
    node = TreeNode.objects.get(path="com.dept1.product2.system2")
    assert not TreeNode.objects.filter(parent_id=node.id).exists()
    assert not node.is_key
    return node


@pytest.fixture
def sys_node(init_tree):
    return TreeNode.objects.get(path="web.system1")


@pytest.fixture
def not_found_path(init_tree):
    path = ".test.not_found"
    assert not TreeNode.objects.filter(path=path).exists()
    return path


@pytest.fixture
def admin_role():
    return Role.objects.create(name="admin", can_manage=True)


@pytest.fixture
def dev_role():
    return Role.objects.create(name="dev")


@pytest.fixture
def employee_user(django_user_model):
    """普通用户"""
    u = django_user_model.objects.create(username="employee")
    u.set_password("12345")
    u.save()
    return u


@pytest.fixture
def employee_client(client, employee_user):
    client.force_login(employee_user)
    return client
