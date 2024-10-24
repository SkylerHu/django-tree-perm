# 接口 API

- 接口遵循 `Restful` 规范；
- 相关数据字段含义和结合数据库 Model 描述查看；

## 1. 管理页面入口

前端管理页面的入口，渲染 `tree_perm/main.html`.

运行服务： `python manage.py runserver 0.0.0.0:8000`

可通过浏览器访问展示及管理页面 `http://localhost:8000/tree/`

## 2. 树结点相关

### 2.1 结点列表

    GET tree/nodes/

##### query 参数

| 字段                     | 类型 | 是否必须 | 默认值 | 说明                        |
| ------------------------ | ---- | -------- | ------ | --------------------------- |
| page                     | int  | 否       | 1      | 页码                        |
| page_size                | int  | 否       | 20     | 每页数据个数                |
| search                   | str  | 否       |        | 根据 name/path 模糊搜索     |
| name                     | str  | 否       |        | 根据字段筛选                |
| disabled                 | int  | 否       |        | 根据字段筛选，取值范围[0,1] |
| is_key                   | int  | 否       |        | 根据字段筛选，取值范围[0,1] |
| parent_id                | int  | 否       |        | 根据字段筛选                |
| parent\_\_path           | str  | 否       |        | 根据字段筛选                |
| path                     | str  | 否       |        | 根据字段筛选                |
| depth                    | int  | 否       |        | 根据字段筛选                |
| alias                    | str  | 否       |        | 根据字段筛选                |
| alias\_\_icontains       | str  | 否       |        | 根据字段筛选                |
| description\_\_icontains | str  | 否       |        | 根据字段筛选                |

##### 返回结果数据

| 字段         | 类型 | 说明                                        |
| ------------ | ---- | ------------------------------------------- |
| count        | int  | 符合条件的总数据                            |
| results      | list | 当前页码下的数据列表                        |
| +id          | int  | ID 主键                                     |
| +name        | str  | 唯一标识                                    |
| +alias       | str  | 别名                                        |
| +description | str  | 描述                                        |
| +parent_id   | str  | 父类 ID                                     |
| +is_key      | bool | 是否 Key 结点（cmdb 场景表示是否是 AppKey） |
| +disabled    | bool | 是否被删除                                  |
| +depth       | str  | 树层级深度                                  |
| +path        | str  | 结点路径                                    |
| +created_at  | str  | 创建时间                                    |
| +updated_at  | str  | 修改时间                                    |

##### 示例

```
GET tree/nodes/?path=com.dept1
```

```json
{
  "count": 1,
  "results": [
    {
      "id": 62,
      "name": "dept1",
      "alias": "部门1",
      "parent_id": 61,
      "is_key": false,
      "path": "com.dept1",
      "disabled": false,
      "description": "",
      "depth": 2,
      "created_at": "2024-10-18 14:35:10",
      "updated_at": "2024-10-18 14:35:10"
    }
  ]
}
```

### 2.2 新增结点

    POST tree/nodes/

`接口权限` 限制为 [has_tree_perm](../Utils/#django_tree_perm.controller.PermManager.has_tree_perm)。

##### Body 参数

| 字段        | 类型 | 是否必须 | 默认值 | 说明                                            |
| ----------- | ---- | -------- | ------ | ----------------------------------------------- |
| name        | str  | 是       |        | 唯一标识                                        |
| alias       | str  | 否       | ""     | 别名                                            |
| description | str  | 否       | ""     | 描述                                            |
| parent_id   | int  | 否       | None   | 父结点 ID，                                     |
| parent_path | str  | 否       | None   | 父结点路径，与 parent_id 都不传递则为新建根结点 |
| is_key      | int  | 否       | False  | 是否关键 Key 结点，取值范围[0,1]                |

##### 示例

```
POST tree/nodes/ -d '{"name": "test", "parent_path": "com.dept1"}'
```

返回状态码为 `201`，返回结构数据格式为字典，与列表中一个子项数据结构一致。

### 2.3 结点详情

    GET tree/nodes/${pk}/

其中 `pk` 传递结点 ID，或者结点 `path` 值

##### 示例

```
GET tree/nodes/62/
GET tree/nodes/com.dept1/
```

返回结构数据格式为字典，与列表中一个子项数据结构一致。

### 2.4 修改结点

    PATCH tree/nodes/${pk}/

`接口权限` 限制为 [has_node_perm](../Utils/#django_tree_perm.controller.PermManager.has_node_perm)，需要当前结点管理权限。

##### Body 参数

| 字段        | 类型 | 是否必须 | 默认值 | 说明                                        |
| ----------- | ---- | -------- | ------ | ------------------------------------------- |
| name        | str  | 否       | None   | 唯一标识                                    |
| alias       | str  | 否       | None   | 别名                                        |
| description | str  | 否       | None   | 描述                                        |
| parent_id   | int  | 否       | None   | 父结点 ID                                   |
| parent_path | str  | 否       | None   | 父结点路径，与 parent_id 必传递其中一个参数 |

何值不为空则修改何值，修改 `parent_id` 或 `parent_path` 的含义是移动结点在树结构中的位置。

##### 示例

```
PATCH tree/nodes/62/ -d '{"name": "test", "parent_path": "com.dept2"}'
```

返回状态码为 `200`，数据结构与详情一致。

### 2.5 删除结点

    DELETE tree/nodes/${pk}/

返回状态码为 `204`，并返回删除之前结点的数据，结构与详情一致。

`接口权限` 限制为 [has_node_perm](../Utils/#django_tree_perm.controller.PermManager.has_node_perm)，需要当前结点管理权限。

### 2.6 按照层级加载结点

    GET tree/lazyload/

##### query 参数

| 字段        | 类型 | 是否必须 | 默认值 | 说明       |
| ----------- | ---- | -------- | ------ | ---------- |
| parent_id   | int  | 否       |        | 父结点 ID  |
| parent_path | str  | 否       |        | 父结点路径 |

- 接口只返回 `disabled=False` 的结点；
- 根据 `parent_id` 或 `parent_path` 返回其所有子结点；
- 没有任何查询参数时，仅返回 `depth=1` 的结点；

使用场景：用于前端实现逐级加载树结构数据。

与结点列表数据返回数据结构一致。

### 2.7 获取树结构数据

    GET tree/load/

##### query 参数

| 字段   | 类型 | 是否必须 | 默认值 | 说明                    |
| ------ | ---- | -------- | ------ | ----------------------- |
| search | str  | 否       |        | 根据 name/path 模糊搜索 |
| path   | str  | 否       |        | 结点路径                |
| depth  | int  | 否       |        | 结点深度                |

- 不传递时，返回所有 `disabled=False` 的结点；
- 传递 query 参数值时，按照结点搜索结果返回数据；
- 返回的数据结构是树结构类型；

##### 返回结果数据

| 字段      | 类型 | 说明                       |
| --------- | ---- | -------------------------- |
| count     | int  | 符合条件的总结点个数       |
| results   | list | 树结构结点数据             |
| +id       | int  | ID 主键                    |
| +name     | str  | 唯一标识                   |
| +path     | str  | 结点路径                   |
| +children | list | 子结点数据，递归树结构展示 |
| +...      | str  | (其他字段)                 |

> 注意：`count` 是符合条件的结点个数，而 `results` 数据为了补全树形结构，会向父类到根结点补全数据，所以数量并不一致。

##### 示例

```
GET tree/load/?search=com.dept1
```

```json
{
  "count": 1,
  "results": [
    {
      "id": 61,
      "name": "com",
      "alias": "公司",
      "parent_id": null,
      "is_key": false,
      "path": "com",
      "children": [
        {
          "id": 62,
          "name": "dept1",
          "alias": "部门1",
          "parent_id": 61,
          "is_key": false,
          "path": "com.dept1"
        }
      ]
    }
  ]
}
```

## 3. 角色相关

### 3.1 角色列表

    GET tree/roles/

##### query 参数

| 字段       | 类型 | 是否必须 | 默认值 | 说明                            |
| ---------- | ---- | -------- | ------ | ------------------------------- |
| page       | int  | 否       | 1      | 页码                            |
| page_size  | int  | 否       | 20     | 每页数据个数                    |
| search     | str  | 否       |        | 根据 name 模糊搜索              |
| name       | str  | 否       |        | 根据角色名称筛选                |
| can_manage | bool | 否       |        | 刷选是否管理角色，取值范围[0,1] |
| key_name   | str  | 否       |        | 关键 Key 结点标识               |
| node_id    | int  | 否       |        | 结点 ID                         |
| path       | str  | 否       |        | 结点路径                        |

传递`key_name` / `node_id` / `path` 其中任意一个字段都能确定一个结点，会返回 node+role 相关联的用户列表 `user_set`.

##### 示例

```
GET tree/roles/?search=ad&key_name=appkey1
```

```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "name": "admin",
      "alias": "管理员",
      "can_manage": true,
      "description": "",
      "created_at": "2024-10-18 14:36:43",
      "updated_at": "2024-10-20 15:34:07",
      "user_set": [
        {
          "id": 18,
          "node_id": 69,
          "role_id": 1,
          "user_id": 2,
          "created_at": "2024-10-24 14:36:15",
          "user": {
            "id": 2,
            "is_superuser": true,
            "username": "skyler",
            "first_name": "",
            "last_name": "",
            "email": "",
            "is_staff": true,
            "is_active": true
          },
          "node": {
            "id": 69,
            "name": "appkey1",
            "alias": "服务1",
            "parent_id": 65,
            "is_key": true,
            "path": "com.dept1.product1.system1.appkey1"
          }
        },
        {
          "id": 17,
          "node_id": 65,
          "role_id": 1,
          "user_id": 3,
          "created_at": "2024-10-20 15:37:45",
          "user": {
            "id": 3,
            "is_superuser": false,
            "username": "user1",
            "first_name": "",
            "last_name": "用户1",
            "email": "",
            "is_staff": false,
            "is_active": true
          },
          "node": {
            "id": 65,
            "name": "system1",
            "alias": "系统1",
            "parent_id": 63,
            "is_key": false,
            "path": "com.dept1.product1.system1"
          }
        }
      ]
    }
  ]
}
```

### 3.2 新增角色

    POST tree/roles/

`接口权限` 限制为 [has_tree_perm](../Utils/#django_tree_perm.controller.PermManager.has_tree_perm)。

##### Body 参数

| 字段        | 类型 | 是否必须 | 默认值 | 说明                        |
| ----------- | ---- | -------- | ------ | --------------------------- |
| name        | str  | 是       |        | 唯一标识                    |
| alias       | str  | 否       | ""     | 别名                        |
| description | str  | 否       | ""     | 描述                        |
| can_manage  | int  | 否       | False  | 是否管理角色，取值范围[0,1] |

##### 示例

```
POST tree/roles/ -d '{"name": "tester", "alias": "测试人员"}'
```

### 3.3 角色详情

    GET tree/roles/${pk}/

也传递`key_name` / `node_id` / `path` 值返回 `user_set` 关联用户数据。

##### 示例

```
GET tree/roles/1/?key_name=appkey1
```

数据结构为列表 results 中的子项。

### 3.4 修改角色

    PATCH tree/roles/${pk}/

`接口权限` 限制为 [has_tree_perm](../Utils/#django_tree_perm.controller.PermManager.has_tree_perm)。

### 3.5 删除角色

    DELETE tree/roles/${pk}/

`接口权限` 限制为 [has_tree_perm](../Utils/#django_tree_perm.controller.PermManager.has_tree_perm)。

## 4. 权限关系相关

### 4.1 关系列表

    GET tree/noderoles/

##### query 参数

| 字段                   | 类型      | 是否必须 | 默认值 | 说明                       |
| ---------------------- | --------- | -------- | ------ | -------------------------- |
| page                   | int       | 否       | 1      | 页码                       |
| page_size              | int       | 否       | 20     | 每页数据个数               |
| search                 | str       | 否       |        | 根据 node\_\_path 模糊搜索 |
| node_id                | int       | 否       |        | 根据字段筛选               |
| node\_\_path           | str       | 否       |        | 根据字段筛选               |
| node\_\_path\_\_in     | list[str] | 否       |        | 根据字段筛选               |
| role_id                | int       | 否       |        | 根据字段筛选               |
| role\_\_name           | str       | 否       |        | 根据字段筛选               |
| role\_\_name\_\_in     | list[str] | 否       |        | 根据字段筛选               |
| user_id                | int       | 否       |        | 根据字段筛选               |
| user\_\_username       | str       | 否       |        | 根据字段筛选               |
| user\_\_username\_\_in | list[str] | 否       |        | 根据字段筛选               |

##### 示例

```
GET tree/noderoles/?search=appkey1
```

```json
{
  "count": 1,
  "results": [
    {
      "id": 18,
      "node_id": 69,
      "role_id": 1,
      "user_id": 2,
      "created_at": "2024-10-24 14:36:15",
      "node": {
        "id": 69,
        "name": "appkey1",
        "alias": "服务1",
        "parent_id": 65,
        "is_key": true,
        "path": "com.dept1.product1.system1.appkey1"
      },
      "role": {
        "id": 1,
        "name": "admin",
        "alias": "管理员",
        "can_manage": true
      },
      "user": {
        "id": 2,
        "is_superuser": true,
        "username": "skyler",
        "first_name": "",
        "last_name": "",
        "email": "",
        "is_staff": true,
        "is_active": true
      }
    }
  ]
}
```

### 4.2 新增关系

    POST tree/noderoles/

`接口权限` 限制为 [has_node_perm](../Utils/#django_tree_perm.controller.PermManager.has_node_perm)，需要相关结点管理权限。

##### Body 参数

| 字段      | 类型      | 是否必须 | 默认值 | 说明                                  |
| --------- | --------- | -------- | ------ | ------------------------------------- |
| node_id   | int       | 否       |        | 结点 ID                               |
| path      | str       | 否       |        | 结点路径，和 node_id 必须传递其一     |
| role_id   | int       | 否       |        | 角色 ID                               |
| role_name | str       | 否       |        | 角色标识，和 role_id 必须传递其一     |
| user_id   | int       | 否       |        | 用户 ID                               |
| user_ids  | list[int] | 否       |        | 用户 ID 列表，和 user_id 必须传递其一 |

### 4.3 关系详情

    GET tree/noderoles/${pk}/

### 4.4 删除关系

    DELETE tree/noderoles/${pk}/

`接口权限` 限制为 [has_node_perm](../Utils/#django_tree_perm.controller.PermManager.has_node_perm)，需要相关结点管理权限。

## 5. 其他

### 5.1 用户列表

    GET tree/users/

### 5.2 用户详情

    GET tree/users/${pk}/

### 5.3 用户登录

    POST tree/perm/

##### Body 参数

| 字段     | 类型 | 是否必须 | 默认值 | 说明   |
| -------- | ---- | -------- | ------ | ------ |
| username | str  | 是       |        | 用户名 |
| password | str  | 是       |        | 密码   |

### 5.4 当前用户详情

    GET tree/perm/

##### query 参数

| 字段     | 类型      | 是否必须 | 默认值 | 说明              |
| -------- | --------- | -------- | ------ | ----------------- |
| path     | str       | 否       |        | 结点路径          |
| key_name | int       | 否       |        | 关键 Key 结点标识 |
| roles    | list[str] | 否       |        | 角色标识列表      |

`path` / `key_name` / `roles` 传递参数，根据结点、角色返回用户相关权限数据.

##### 返回结果数据

| 字段          | 类型 | 说明                   |
| ------------- | ---- | ---------------------- |
| user          | dict | 用户信息               |
| +username     | str  | 用户标识               |
| +tree_manager | bool | 是否有树管理权限       |
| +node_manager | bool | 是否有当前结点管理权限 |
| +node_perm    | bool | 是否有当前结点的权限   |
| +...          | str  | (其他字段)             |

#### 示例

```
GET tree/perm/?path=com.dept1.product1.system1
```

```json
{
  "user": {
    "id": 3,
    "is_superuser": false,
    "username": "user1",
    "first_name": "",
    "last_name": "",
    "email": "",
    "is_staff": false,
    "is_active": true,
    "tree_manager": false,
    "node_manager": false,
    "node_perm": true
  }
}
```
