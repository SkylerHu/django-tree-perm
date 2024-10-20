#!/usr/bin/env python
# coding=utf-8
import pytest

from django_tree_perm.controller import PermManager, TreeNodeManger
from django_tree_perm.models import NodeRole
from django_tree_perm.exceptions import PermDenyException


@pytest.mark.django_db()
def test_tree_perm(employee_user, admin_user):
    assert PermManager.has_tree_perm(employee_user) is False

    assert PermManager.has_tree_perm(admin_user) is True
    admin_user.is_active = False
    admin_user.save()
    assert PermManager.has_tree_perm(admin_user) is False


@pytest.mark.django_db()
def test_node_perm(admin_user, employee_user, dept_node, key_node, dev_role, admin_role, not_found_path):
    # 超管所有结点权限
    assert PermManager.has_node_perm(admin_user, can_manage=True) is True

    # 用户不对
    assert PermManager.has_node_perm(None) is False

    PermManager.has_node_perm(employee_user) is False
    PermManager.has_node_perm(employee_user, path=not_found_path) is False

    # 默认无权限
    assert PermManager.has_node_perm(employee_user, path=dept_node.path) is False
    assert PermManager.has_node_perm(employee_user, key_name=key_node.name) is False
    # 增加角色
    NodeRole.objects.get_or_create(user=employee_user, node=dept_node, role=dev_role)
    # 当前结点及其子结点都有权限
    assert PermManager.has_node_perm(employee_user, path=dept_node.path) is True
    assert PermManager.has_node_perm(employee_user, key_name=key_node.name) is True
    # 任意一个角色有权限即为有权限
    assert PermManager.has_node_perm(employee_user, path=key_node.path, roles=[admin_role.name, dev_role.name]) is True

    assert PermManager.has_node_perm(employee_user, path=dept_node.path, roles=[admin_role.name]) is False
    # 是否管理权限
    assert PermManager.has_node_perm(employee_user, path=dept_node.path, can_manage=True) is False
    assert PermManager.has_node_perm(employee_user, key_name=key_node.name, can_manage=True) is False
    # 增加管理角色
    NodeRole.objects.get_or_create(user=employee_user, node=dept_node, role=admin_role)
    assert PermManager.has_node_perm(employee_user, path=dept_node.path, can_manage=True) is True
    assert PermManager.has_node_perm(employee_user, key_name=key_node.name, can_manage=True) is True

    # 结点被删除
    TreeNodeManger(node=key_node).remove()
    assert PermManager.has_node_perm(employee_user, key_name=key_node.name) is False


@pytest.mark.django_db()
def test_node_add(employee_user, dept_node, admin_role):
    with pytest.raises(PermDenyException, match="Only superuser can add a new root node"):
        TreeNodeManger.add_node("test", user=employee_user)

    with pytest.raises(PermDenyException, match="No add permission"):
        TreeNodeManger.add_node("test", parent=dept_node, user=employee_user)

    NodeRole.objects.get_or_create(user=employee_user, node=dept_node, role=admin_role)
    # 管理角色也无法新增根结点
    with pytest.raises(PermDenyException, match="Only superuser can add a new root node"):
        TreeNodeManger.add_node("test", user=employee_user)

    TreeNodeManger.add_node("test", parent=dept_node, user=employee_user)


@pytest.mark.django_db()
def test_node_update(employee_user, dept_node, dev_role, admin_role):
    with pytest.raises(PermDenyException, match="No update permission"):
        TreeNodeManger(node=dept_node, user=employee_user).update_attrs(alias="test")

    NodeRole.objects.get_or_create(user=employee_user, node=dept_node, role=dev_role)
    with pytest.raises(PermDenyException, match="No update permission"):
        TreeNodeManger(node=dept_node, user=employee_user).update_attrs(alias="test")

    NodeRole.objects.get_or_create(user=employee_user, node=dept_node, role=admin_role)
    TreeNodeManger(node=dept_node, user=employee_user).update_attrs(alias="test")


@pytest.mark.django_db()
def test_node_move(employee_user, key_node, dept_node, admin_role):
    with pytest.raises(PermDenyException, match="No move permission for the path"):
        TreeNodeManger(node=key_node, user=employee_user).move_path(parent_path=dept_node.path)

    NodeRole.objects.get_or_create(user=employee_user, node=key_node, role=admin_role)

    with pytest.raises(PermDenyException, match="No move permission for the parent path"):
        TreeNodeManger(node=key_node, user=employee_user).move_path(parent_path=dept_node.path)

    NodeRole.objects.get_or_create(user=employee_user, node=dept_node, role=admin_role)
    TreeNodeManger(node=key_node, user=employee_user).move_path(parent_path=dept_node.path)


@pytest.mark.django_db()
def test_node_remove(employee_user, key_node, dept_node, admin_role):
    with pytest.raises(PermDenyException, match="No remove permission"):
        TreeNodeManger(node=key_node, user=employee_user).remove()

    NodeRole.objects.get_or_create(user=employee_user, node=dept_node, role=admin_role)
    TreeNodeManger(node=key_node, user=employee_user).remove()
