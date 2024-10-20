#!/usr/bin/env python
# coding=utf-8
import pytest

from http import HTTPStatus
from django.test import Client


from django_tree_perm.models import TreeNode, NodeRole, Role
from django_tree_perm.controller import PermManager
from django_tree_perm.views import base as base_v


def test_main_view(client):
    resp = client.get("")
    assert resp.status_code == HTTPStatus.OK
    assert "text/html" in resp.headers.get("Content-Type")


@pytest.mark.django_db()
def test_csrf(settings, employee_user, dept_node, admin_role):
    settings.MIDDLEWARE.insert(3, "django.middleware.csrf.CsrfViewMiddleware")

    NodeRole.objects.create(node=dept_node, user=employee_user, role=admin_role)

    client = Client(enforce_csrf_checks=True)
    client.force_login(employee_user)

    data = {"name": "leader", "parent_id": dept_node.id}

    # 无令牌禁止访问
    resp = client.post("/tree/nodes/", data=data)
    assert resp.status_code == HTTPStatus.FORBIDDEN, resp.content

    # 获取令牌并重新请求
    resp = client.get("")
    csrf_token = resp.cookies["csrftoken"].value
    data["csrfmiddlewaretoken"] = csrf_token
    resp = client.post("/tree/nodes/", data=data)
    assert resp.status_code == HTTPStatus.CREATED, resp.content


@pytest.mark.django_db()
def test_perm_view(client, employee_user):
    # 未登录
    resp = client.get("/tree/perm/")
    assert resp.status_code == HTTPStatus.UNAUTHORIZED, resp.content
    # 登录用户
    login_resp = client.post("/tree/perm/", data={"username": employee_user.username, "password": "123"})
    assert login_resp.status_code == HTTPStatus.BAD_REQUEST, login_resp.content
    login_resp = client.post(
        "/tree/perm/",
        data={"username": employee_user.username, "password": "12345"},
        content_type="application/json",
    )
    assert login_resp.status_code == HTTPStatus.OK, login_resp.content
    # 登录成功后
    resp = client.get("/tree/perm/")
    assert resp.status_code == HTTPStatus.OK, resp.content


@pytest.mark.django_db()
def test_perm_params(employee_client, employee_user, key_node, admin_role, dev_role):
    NodeRole.objects.create(node=key_node, user=employee_user, role=dev_role)
    params = {"path": key_node.path, "key_name": key_node.name, "roles": ",".join([admin_role.name, dev_role.name])}
    resp = employee_client.get("/tree/perm/", data=params)
    assert resp.status_code == HTTPStatus.OK, resp.content
    data = resp.json()["user"]
    assert data["tree_manager"] is False
    assert data["node_manager"] is False
    assert data["node_perm"] is True


@pytest.mark.django_db()
@pytest.mark.parametrize(
    "query_params,count",
    [
        ({"name": "not-found"}, 0),
        ({"disabled": 1}, 0),
        ({"disabled": 0}, 20),
        ({"is_key": 1}, 6),
        ({"parent_id": "-"}, 6),
        ({"parent__path": "-"}, 6),
        ({"path": "-"}, 1),
        ({"depth": 2}, 3),
        ({"alias__icontains": "-"}, 2),
        ({"search": "sys"}, 1),
        ({"user_id": 1}, 0),
    ],
)
def test_node_list(employee_client, dept_node, query_params, count):
    # 处理下参数
    if "path" in query_params:
        query_params["path"] = dept_node.path
    if "parent_id" in query_params:
        query_params["parent_id"] = dept_node.id
    if "parent__path" in query_params:
        query_params["parent__path"] = dept_node.path
    if "alias__icontains" in query_params:
        query_params["alias__icontains"] = dept_node.alias[:-1]

    # get函数低版本不支持 query_params 为key作为传递参数, 5.1版本新增
    resp = employee_client.get("/tree/nodes/", data=query_params)
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["count"] == count


@pytest.mark.django_db()
def test_op_node(employee_client, employee_user, dept_node, admin_role):
    # 无权限也可以获取获取
    assert not PermManager.has_node_perm(user=employee_user, path=dept_node.path)
    resp = employee_client.get(f"/tree/nodes/{dept_node.path}/")
    assert resp.status_code == HTTPStatus.OK, resp.content
    assert resp.json()["id"] == dept_node.id

    data = {
        "parent_id": dept_node.id,
        "name": "product_test",
    }

    # 测试无权限
    resp = employee_client.post("/tree/nodes/", data=data)
    assert resp.status_code == HTTPStatus.FORBIDDEN
    resp = employee_client.patch(
        f"/tree/nodes/{dept_node.id}/", data={"alias": "测试"}, content_type="application/json"
    )
    assert resp.status_code == HTTPStatus.FORBIDDEN

    # 添加管理权限
    NodeRole.objects.create(node=dept_node, role=admin_role, user=employee_user)

    # 新增
    resp = employee_client.post("/tree/nodes/", data=data)
    assert resp.status_code == HTTPStatus.CREATED, resp.content
    node_id = resp.json()["id"]
    new_node = TreeNode.objects.get(id=node_id)
    assert new_node.parent_id == dept_node.id

    # 修改
    with pytest.raises(NotImplementedError, match="not support content-type"):
        employee_client.patch(f"/tree/nodes/{new_node.id}/", data={"alias": "测试"})
    resp = employee_client.patch(f"/tree/nodes/{new_node.id}/", data={"alias": "测试"}, content_type="application/json")
    assert resp.status_code == HTTPStatus.OK, resp.content
    new_node.refresh_from_db()
    assert new_node.alias == "测试"

    # 无删除权限
    NodeRole.objects.filter(node=dept_node, role=admin_role, user=employee_user).delete()
    resp = employee_client.delete(f"/tree/nodes/{new_node.id}/")
    assert resp.status_code == HTTPStatus.FORBIDDEN
    NodeRole.objects.create(node=dept_node, role=admin_role, user=employee_user)
    # 删除
    resp = employee_client.delete(f"/tree/nodes/{new_node.id}/")
    assert resp.status_code == HTTPStatus.NO_CONTENT, resp.content
    assert not TreeNode.objects.filter(id=node_id).exists()


@pytest.mark.django_db()
def test_lazy_load(employee_client, dept_node):
    expect_count = TreeNode.objects.filter(depth=1).count()
    resp = employee_client.get("/tree/lazyload/")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json()["count"] == expect_count

    resp = employee_client.get("/tree/lazyload/", data={"parent_id": dept_node.id})
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert resp.json()["count"] == 6

    resp = employee_client.get("/tree/lazyload/", data={"parent_path": dept_node.path})
    assert resp.status_code == HTTPStatus.OK
    assert data == resp.json()


@pytest.mark.django_db()
@pytest.mark.usefixtures("init_tree")
@pytest.mark.parametrize(
    "query_params,count,node_num",
    [
        ({}, 20, 20),
        ({"path": "com.dept1"}, 1, 2),
        ({"depth": 2}, 5, 5),
        ({"search": "sys"}, 1, 2),
    ],
)
def test_tree_load(employee_client, query_params, count, node_num):

    def get_tree_nodes(tree_data):
        count = 0
        for item in tree_data:
            count += 1
            children = item.get("children") or []
            if not children:
                continue
            count += get_tree_nodes(children)
        return count

    resp = employee_client.get("/tree/load/", data=query_params)
    data = resp.json()
    assert data["count"] == count
    assert get_tree_nodes(data["results"]) == node_num


@pytest.mark.django_db()
def test_fetch_user(employee_client, admin_user, employee_user):
    resp = employee_client.get("/tree/users/")
    assert resp.status_code == HTTPStatus.OK
    u_ids = sorted([u["id"] for u in resp.json()["results"]])
    expect_ids = [employee_user.id, admin_user.id]
    assert len(u_ids) == len(expect_ids)
    assert u_ids == sorted(expect_ids)
    # 搜索
    resp = employee_client.get("/tree/users/", data={"search": "emp"})
    assert resp.status_code == HTTPStatus.OK
    assert resp.json()["count"] == 1
    # 详情
    resp = employee_client.get(f"/tree/users/{employee_user.username}/")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json()["id"] == employee_user.id


@pytest.mark.django_db()
def test_op_role(employee_client, admin_client, employee_user, dept_node):
    resp = employee_client.post("/tree/roles/", data={"name": "leader"})
    assert resp.status_code == HTTPStatus.FORBIDDEN, resp.content
    # 新增
    resp = admin_client.post("/tree/roles/", data={"name": "leader"})
    assert resp.status_code == HTTPStatus.CREATED
    role_id = resp.json()["id"]
    role = Role.objects.get(id=role_id)
    # 普通用户可以查看详情
    resp = employee_client.get(f"/tree/roles/{role.id}/")
    assert resp.status_code == HTTPStatus.OK

    # 修改
    resp = employee_client.patch(f"/tree/roles/{role.id}/", data={"alias": "leader"}, content_type="application/json")
    assert resp.status_code == HTTPStatus.FORBIDDEN, resp.content
    resp = admin_client.patch(f"/tree/roles/{role.id}/", data={"alias": "leader"}, content_type="application/json")
    assert resp.status_code == HTTPStatus.OK
    role.refresh_from_db()
    assert role.alias == "leader", resp.json

    # 删除
    resp = employee_client.delete(f"/tree/roles/{role.id}/")
    assert resp.status_code == HTTPStatus.FORBIDDEN, resp.content
    # 有权限也不让删除还有关联用户的角色
    NodeRole.objects.create(node=dept_node, user=employee_user, role=role)
    resp = admin_client.delete(f"/tree/roles/{role.id}/")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    # 清除关联用户再删除
    NodeRole.objects.filter(node=dept_node, role=role).delete()
    resp = admin_client.delete(f"/tree/roles/{role.id}/")
    assert resp.status_code == HTTPStatus.NO_CONTENT
    assert not Role.objects.filter(id=role_id).exists()


@pytest.mark.django_db()
def test_node_role(admin_client, employee_client, django_user_model, dept_node, key_node, dev_role, employee_user):
    data = {
        "node_id": dept_node.id,
        "role_id": dev_role.id,
        "user_id": employee_user.id,
    }

    assert PermManager.has_node_perm(employee_user, path=dept_node.path, can_manage=True) is False
    resp = employee_client.post("/tree/noderoles/", data=data)
    assert resp.status_code == HTTPStatus.FORBIDDEN, resp.content

    resp = admin_client.post("/tree/noderoles/", data=data)
    assert resp.status_code == HTTPStatus.CREATED
    node_role = NodeRole.objects.get(id=resp.json()["id"])

    # 查看列表
    resp = employee_client.get("/tree/noderoles/")
    assert resp.status_code == HTTPStatus.OK, resp.content
    assert resp.json()["count"] == 1
    # 搜索
    resp = employee_client.get("/tree/noderoles/", data={"node__path__in": "a.b.c"})
    assert resp.status_code == HTTPStatus.OK, resp.content
    assert resp.json()["count"] == 0
    resp = employee_client.get("/tree/noderoles/", data={"key_names": key_node.name})
    assert resp.status_code == HTTPStatus.OK, resp.content
    assert resp.json()["count"] == 0

    # 一次关联多个用户
    user = django_user_model.objects.create(username="test")
    data = {
        "node_id": key_node.id,
        "role_id": dev_role.id,
        "user_ids": [employee_user.id, user.id],
    }
    resp = admin_client.post("/tree/noderoles/", data=data)
    assert resp.status_code == HTTPStatus.CREATED, resp.content
    # 实际新增一个
    assert resp.json()["count"] == 2
    resp = admin_client.post("/tree/noderoles/", data=data, content_type="application/json")
    assert resp.json()["count"] == 0
    # 查找
    resp = employee_client.get("/tree/noderoles/", data={"key_names": key_node.name})
    assert resp.json()["count"] == 2

    # 查看
    resp = employee_client.get(f"/tree/noderoles/{node_role.id}/")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json()["id"] == node_role.id

    # 删除
    resp = employee_client.delete(f"/tree/noderoles/{node_role.id}/")
    assert resp.status_code == HTTPStatus.FORBIDDEN, resp.content
    resp = admin_client.delete(f"/tree/noderoles/{node_role.id}/")
    assert resp.status_code == HTTPStatus.NO_CONTENT, resp.content

    # 不允许修改
    resp = employee_client.patch(f"/tree/noderoles/{node_role.id}/")
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED, resp.content


def test_common_view(client, admin_client, dev_role):
    # 测试接口要登录
    resp = client.get(f"/tree/roles/{dev_role.id}/")
    assert resp.status_code == HTTPStatus.FORBIDDEN, resp.content
    resp = admin_client.get(f"/tree/roles/{dev_role.id}/")
    assert resp.status_code == HTTPStatus.OK, resp.content

    # 测试接口参数错误
    resp = admin_client.post("/tree/nodes/", data={"name": ".not-found"})
    assert resp.status_code == HTTPStatus.BAD_REQUEST, resp.content


@pytest.mark.django_db()
def test_base_view(rf, admin_user, dev_role):
    class TestView(base_v.BaseModelView):
        pass

    with pytest.raises(NotImplementedError, match="model cannot be empty"):
        TestView.as_view()

    # test for check_create_permission
    request = rf.post("/tree/roles/", data={"name": "test"})
    request.user = admin_user

    class TestRoleCreateView(base_v.BaseCreateModelMixin):
        model = Role

    resp = TestRoleCreateView.as_view()(request)
    assert resp.status_code == HTTPStatus.CREATED, resp.content

    # test for check_object_permissions
    request = rf.patch(f"/tree/roles/{dev_role.id}/", data={"alias": "test"}, content_type="application/json")
    request.user = admin_user

    class TestRoleEditView(base_v.BaseUpdateModelMixin):
        model = Role

    resp = TestRoleEditView.as_view()(request, pk=dev_role.id)
    assert resp.status_code == HTTPStatus.OK, resp.content
