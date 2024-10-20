#!/usr/bin/env python
# coding=utf-8
import pytest

from django.core.exceptions import ValidationError
from django_tree_perm import utils
from django_tree_perm.exceptions import ParamsValidateException
from django_tree_perm.controller import TreeNodeManger
from django_tree_perm.models import TreeNode


@pytest.mark.django_db()
@pytest.mark.usefixtures("init_tree")
@pytest.mark.parametrize(
    "params",
    [
        {"name": "root", "alias": "根结点"},
        {"name": "test_product", "description": "测试产品结点", "parent_path": "com.dept1"},
        {"name": "test_key", "is_key": True, "parent_path": "com.dept1"},
    ],
)
def test_add_success(params):
    name = params.pop("name")
    manager = TreeNodeManger.add_node(name, **params)
    assert manager.node.id is not None


@pytest.mark.django_db()
@pytest.mark.usefixtures("init_tree")
@pytest.mark.parametrize(
    "params,exception,error",
    [
        ({"name": "r"}, ValidationError, "由小写字母、数字、中横线、下划线组成"),
        ({"name": ""}, ParamsValidateException, "Node name cannot be empty"),
        ({"name": "root.node"}, ParamsValidateException, "is not allowed to contain separator"),
        ({"name": "root", "parent": -1}, ParamsValidateException, "must be a TreeNode"),
        ({"name": "root", "is_key": True}, ParamsValidateException, "not allowed to be root node"),
    ],
)
def test_add_error(params, exception, error):
    with pytest.raises(exception, match=error):
        name = params.pop("name", None)
        TreeNodeManger.add_node(name, **params)


@pytest.mark.django_db()
def test_update_node(dept_node, sys_node):
    manager = TreeNodeManger(node=dept_node)
    manager.update_attrs(name=dept_node.name)
    manager.update_attrs(name=f"{dept_node.name}2", alias="测试alias", description="测试desc")
    # 测试更改父类路径
    assert dept_node.parent_id != sys_node.id
    manager.update_attrs(parent_id=sys_node.id)
    assert dept_node.parent_id == sys_node.id
    # 不允许name中有分隔符
    with pytest.raises(ParamsValidateException, match="is not allowed to contain separator"):
        manager.update_attrs(name=f"{dept_node.name}{utils.TREE_SPLIT_NODE_FLAG}2")


@pytest.mark.django_db()
def test_update_key_node(key_node):
    manager = TreeNodeManger(node=key_node)
    manager.update_attrs(alias="测试alias", description="测试desc")
    # key node 不允许修改name
    with pytest.raises(ParamsValidateException, match="The key node does not allow edit name"):
        manager.update_attrs(name=f"{key_node.name}2")


@pytest.mark.django_db()
def test_move_node(dept_node, sys_node):
    manager = TreeNodeManger(path=dept_node.path)

    queryset = manager.node.get_self_and_children()
    expect_count = queryset.count()

    # 挪移到当前位置
    rows = manager.move_path(parent_path=dept_node.parent.path)
    assert rows == 0

    with pytest.raises(ParamsValidateException, match="Cannot be its own child node"):
        manager.move_path(parent_id=dept_node.id)

    # 找到dept的子结点
    child = TreeNode.objects.filter(parent=dept_node).first()
    assert child is not None
    with pytest.raises(ParamsValidateException, match="Cannot be its own child node"):
        manager.move_path(parent_id=child.id)

    rows = manager.move_path(parent_path=sys_node.path)
    assert expect_count == rows
    dept_node.refresh_from_db()
    assert dept_node.path == utils.TREE_SPLIT_NODE_FLAG.join([sys_node.path, dept_node.name])


@pytest.mark.django_db()
def test_remove_node(root_node, dept_node, key_node, no_child_node):
    manager = TreeNodeManger(node=dept_node)

    queryset = manager.node.get_self_and_children()
    expect_count = queryset.filter(is_key=False).count()

    with pytest.raises(ParamsValidateException, match="Deleting nodes that have child nodes is not allowed"):
        # 有子结点不允许被直接删除
        manager.remove()

    assert key_node.disabled is False
    assert TreeNode.objects.filter(parent_id=dept_node.id).exists()
    rows = manager.remove(clear_chidren=True)
    assert rows == expect_count
    # 叶子key结点置为disabled
    key_node.refresh_from_db()
    assert key_node.disabled is True
    # 自身和子结点会被删除
    assert not TreeNode.objects.filter(path=dept_node.path).exists()
    assert not TreeNode.objects.filter(parent_id=dept_node.id).exists()

    # 删除无子结点的结点
    manager = TreeNodeManger(node=no_child_node)
    rows = manager.remove()
    assert rows == 1
    assert not TreeNode.objects.filter(path=no_child_node.path).exists()

    # 删除带子结点但无key结点的根结点
    assert TreeNode.objects.filter(path__startswith=root_node.path_prefix).exists()
    TreeNode.objects.filter(is_key=True, path__startswith=root_node.path_prefix).delete()
    TreeNodeManger(path=root_node.path).remove(clear_chidren=True)
    assert not TreeNode.objects.filter(path=root_node.path).exists()


@pytest.mark.django_db()
def test_remove_key_node(key_node):
    assert key_node.disabled is False
    manager = TreeNodeManger(node=key_node)
    rows = manager.remove()
    assert rows == 0
    # 删除后记录还存在
    key_node.refresh_from_db()
    assert key_node.disabled is True

    with pytest.raises(ParamsValidateException, match="The node has been disabled"):
        # 已删除不能被重复执行
        manager.remove()


@pytest.mark.django_db()
def test_get_node(dept_node, key_node, not_found_path):
    with pytest.raises(ParamsValidateException, match="must be a TreeNode instance"):
        TreeNodeManger.get_node_object(node=1)

    assert TreeNodeManger.get_node_object(node=dept_node) == dept_node
    assert TreeNodeManger.get_node_object(node_id=dept_node.id).path == dept_node.path
    assert TreeNodeManger.get_node_object(path=dept_node.path).id == dept_node.id

    assert TreeNodeManger.get_node_object(path=not_found_path) is None
    with pytest.raises(ParamsValidateException, match="cannot be null"):
        TreeNodeManger.get_node_object(path=not_found_path, required=True)

    assert TreeNodeManger.get_node_object(key_name=key_node.name) == key_node
    with pytest.raises(ParamsValidateException, match="not allowed to be a parent node"):
        TreeNodeManger.find_parent_node(parent_path=key_node.path)
    TreeNodeManger(node=key_node).remove()
    with pytest.raises(ParamsValidateException, match="This node is disabled"):
        TreeNodeManger.get_node_object(key_name=key_node.name)
