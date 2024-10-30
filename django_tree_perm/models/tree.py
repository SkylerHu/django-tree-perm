#!/usr/bin/env python
# coding=utf-8
import typing
import hashlib

from django.db import models
from django.core.validators import RegexValidator

from django_tree_perm.utils import TREE_SPLIT_NODE_FLAG, get_tree_paths
from .manager import TreeNodeManager, TreeNodeQuerySet
from .utils import User, user_to_json, format_datetime_field


def tree_validator() -> RegexValidator:
    regex = RegexValidator(
        r"^[a-z]([a-z0-9_-]){0,62}[a-z0-9]$",
        message="由小写字母、数字、中横线、下划线组成，字母开头、字母或数据结尾，长度范围为2~64",
    )
    return regex


class TreeNode(models.Model):
    """树结点数据模型

    表结构设计如下：

    | 字段        | 类型          | 描述              | 默认值  | 其他说明                             |
    | ----------- | ------------- | ----------------- | ------- | ------------------------------------ |
    | id          | bigint        | 主键              |         | pk(primary key), 自增                |
    | name        | varchar(64)   | 唯一标识          |         | unique                               |
    | alias       | varchar(64)   | 别名              | `""`    |                                      |
    | description | varchar(1024) | 描述              | `""`    |                                      |
    | parent_id   | bigint        | 父类结点          | `null`  | fk(foreign key) , 为 null 时为根结点 |
    | is_key      | tinyint(1)    | 作为 key 关键结点 | `False` | is_key=True 时 CMDB 中为 AppKey 结点 |
    | disabled    | tinyint(1)    | 是否标记删除      | `False` | 避免 is_key=True 的结点被二次创建    |
    | path        | varchar(191)  | 树结点完整路径    |         |
    | depth       | smallint      | 树结点深度        | `1`     |                                      |
    | node_hash   | 结点哈希值    | 保证唯一值        |         | path 全局唯一 ，且is_key=True时name全局唯一 |
    | created_at  | datetime(6)   | 创建时间          |         |                                      |
    | updated_at  | datetime(6)   | 更新时间          |         |                                      |


    Tip: 注意
        - `name` 校验规则详见[validator](./#django_tree_perm.models.tree.tree_validator)
        - `node_hash` 是因为mysql不支持条件唯一约束，而设计产生的。

    Tip: `TREE_SPECIAL_FIELDS`
        定义特殊字段，这些字段不主动赋值；调用 `validate_save` 保存会自动更新相关字段，详见函数 `patch_attrs` 。
    """

    TREE_SPECIAL_FIELDS = ("path", "depth", "node_hash", "updated_at")

    class Meta:
        app_label = "django_tree_perm"
        verbose_name = "树结点"
        ordering = ("path",)
        indexes = [
            models.Index(fields=["is_key", "disabled", "name"]),
        ]

    name = models.CharField(verbose_name="标识", max_length=64, db_index=True, validators=[tree_validator()])
    alias = models.CharField(verbose_name="别名", max_length=64, default="", blank=True)
    description = models.CharField(verbose_name="描述", max_length=1024, default="", blank=True)
    # 父类结点为空时，表示是树的根结点
    parent = models.ForeignKey(
        "self",
        verbose_name="父类结点",
        related_name="children",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    # is_key=True的结点 为 绝对叶子结点，不允许新增子结点；应用场景AppKey
    is_key = models.BooleanField(verbose_name="作为Key", default=False)
    # 叶子结点不可以删除，仅用于叶子结点
    disabled = models.BooleanField(verbose_name="是否禁用", default=False, db_index=True)
    # 以下字段不允许直接赋值更新
    path = models.CharField(verbose_name="结点路径", max_length=191, default="", db_index=True, blank=True)
    # 树的根结点深度为1
    depth = models.SmallIntegerField(verbose_name="深度", default=1)
    # 为了保证叶子结点name全局唯一，且有些数据库例如mysql不支持 UniqueConstraint按照条件约束
    node_hash = models.CharField(
        verbose_name="结点哈希值",
        unique=True,
        max_length=32,
        db_index=True,
        error_messages={
            "unique": "结点已存在，请更换标识",
        },
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("修改时间", auto_now=True)

    objects = TreeNodeManager.from_queryset(TreeNodeQuerySet)()

    def __str__(self) -> str:
        return f"TreeNode:{self.id} {self.path}"

    def to_json(self, partial: bool = False) -> dict:
        """将model数据转换成可序列化的JSON数据

        Args:
            partial: 是否返回部分数据.

        Returns:
            返回JSON数据
        """
        data = {
            "id": self.id,
            "name": self.name,
            "alias": self.alias,
            "parent_id": self.parent_id,
            "is_key": self.is_key,
            "path": self.path,
        }
        if not partial:
            data.update(
                {
                    "disabled": self.disabled,
                    "description": self.description,
                    "depth": self.depth,
                    "created_at": format_datetime_field(self.created_at),
                    "updated_at": format_datetime_field(self.updated_at),
                }
            )
        return data

    @property
    def path_prefix(self) -> str:
        """结点路径作为前缀查询其所有子结点时的场景使用

        例如有结点：a.bb.c / a.b.c / a.b.c.d

        查询结点 a.b 的所有子结点，不能够用 startsiwth("a.b") 而是 startsiwth("a.b.")

        Returns:
            字符串
        """
        return f"{self.path}{TREE_SPLIT_NODE_FLAG}"

    def get_self_and_children(self) -> TreeNodeQuerySet:
        """查询自身及其所有子结点，包含孙子结点

        查询条件为：path=self.path | path__startswith=self.path_prefix

        Returns:
            返回一个查询对象
        """
        qs = TreeNode.objects.filter(models.Q(path=self.path) | models.Q(path__startswith=self.path_prefix))
        return qs

    def patch_attrs(self) -> None:
        """处理更新 `TREE_SPECIAL_FIELDS` 中定义字段的值

        - `path` 根据结点层级 name 拼接而来
        - `depth` 计算树结点深度，根结点深度为1
        - `node_hash` 保证全局唯一的约束
            - path全局唯一
            - is_key=True是，name字段全局唯一
        """
        # 初始化path
        path = self.path
        if self.disabled:
            self.path = ""
        elif self.parent_id:
            path = TREE_SPLIT_NODE_FLAG.join([self.parent.path, self.name])
        else:
            path = self.name
        self.path = path
        # 初始化树结点深度
        self.depth = len(self.path.split(TREE_SPLIT_NODE_FLAG))
        # 更新node_hash
        _value = self.path
        if self.disabled:
            # 因为name必须是字母开头，所以不会和pk重复
            _value = str(self.pk)
        elif self.is_key:
            # 叶子结点需要保证name全局唯一
            _value = self.name
        _hash = hashlib.md5(_value.encode("utf-8")).hexdigest()
        self.node_hash = _hash

    def validate_save(self) -> None:
        """更新特殊字段并校验数据合法性后进行保存"""
        self.patch_attrs()
        self.full_clean()
        self.save()


class Role(models.Model):
    """
    结点角色

    一种角色代表一种或者一类权限。

    表结构设计如下：

    | 字段        | 类型          | 描述         | 默认值  | 其他说明                                              |
    | ----------- | ------------- | ------------ | ------- | ----------------------------------------------------- |
    | id          | bigint        | 主键         |         | pk(primary key), 自增                                 |
    | name        | varchar(64)   | 唯一标识     |         | unique, 具体校验详见[tree_validator](#tree_validator) |
    | alias       | varchar(64)   | 别名         | `""`    |                                                       |
    | description | varchar(1024) | 描述         | `""`    |                                                       |
    | can_manage  | tinyint(1)    | 允许管理结点 | `False` | 赋予该角色后，可以管理当前结点上的人员角色关系        |
    | created_at  | datetime(6)   | 创建时间     |         |                                                       |
    | updated_at  | datetime(6)   | 更新时间     |         |                                                       |

    """

    class Meta:
        app_label = "django_tree_perm"
        verbose_name = "角色"

    name = models.CharField(
        verbose_name="唯一标识", max_length=64, db_index=True, unique=True, validators=[tree_validator()]
    )
    alias = models.CharField(verbose_name="显示名称", max_length=64, default="", blank=True)
    description = models.CharField(verbose_name="描述", max_length=1024, default="", blank=True)
    # 赋予该角色后，可以管理当前结点上的人员角色关系
    can_manage = models.BooleanField(verbose_name="允许管理结点", default=False)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("修改时间", auto_now=True)

    def to_json(self, partial: bool = False, path: typing.Optional[str] = None) -> dict:
        """将model数据转换成可序列化的JSON数据

        Args:
            partial: 是否返回部分数据.
            path: 结点路径，传递后将返回当前结点下有角色权限的用户，从父类结点继承的角色也算

        Returns:
            返回JSON数据
        """
        data = {
            "id": self.id,
            "name": self.name,
            "alias": self.alias,
            "can_manage": self.can_manage,
        }
        if not partial or path:
            data.update(
                {
                    "description": self.description,
                    "created_at": format_datetime_field(self.created_at),
                    "updated_at": format_datetime_field(self.updated_at),
                }
            )
            if path:
                paths = get_tree_paths(path)
                node_role_qs = NodeRole.objects.filter(node__path__in=paths, role_id=self.id).select_related(
                    "user", "node"
                )
                data["user_set"] = []
                for row in node_role_qs.order_by("-node__path"):
                    item = row.to_json(partial=True)
                    item.update(
                        {
                            "user": user_to_json(row.user),
                            "node": row.node.to_json(partial=True),
                        }
                    )
                    data["user_set"].append(item)
        return data


class NodeRole(models.Model):
    """结点+角色+用户 关联关系

    表结构设计如下：

    | 字段       | 类型        | 描述     | 默认值 | 其他说明              |
    | ---------- | ----------- | -------- | ------ | --------------------- |
    | id         | bigint      | 主键     |        | pk(primary key), 自增 |
    | node_id    | bigint      | 结点     |        | fk(foreign key), 自增 |
    | role_id    | bigint      | 角色     |        | fk(foreign key), 自增 |
    | user_id    | bigint      | 用户     |        | fk(foreign key), 自增 |
    | created_at | datetime(6) | 创建时间 |        |                       |
    """

    class Meta:
        app_label = "django_tree_perm"
        verbose_name = "结点角色关系"
        unique_together = ("node", "role", "user")

    node = models.ForeignKey(TreeNode, on_delete=models.CASCADE, related_name="noderole_set")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="noderole_set")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="noderole_set")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    def to_json(self, partial: bool = False) -> dict:
        """将model数据转换成可序列化的JSON数据

        Args:
            partial: 默认返回简单数据，否则返回node/role/user具体实例信息.

        Returns:
            返回JSON数据
        """
        data = {
            "id": self.id,
            "node_id": self.node_id,
            "role_id": self.role_id,
            "user_id": self.user_id,
            "created_at": format_datetime_field(self.created_at),
        }
        if not partial:
            data.update(
                {
                    "node": self.node.to_json(partial=True),
                    "role": self.role.to_json(partial=True),
                    "user": user_to_json(self.user),
                }
            )
        return data
