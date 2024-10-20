#!/usr/bin/env python
# coding=utf-8
import hashlib

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

from django_tree_perm import settings
from django_tree_perm.utils import TREE_SPLIT_NODE_FLAG, get_tree_paths
from .manager import TreeNodeManager, TreeNodeQuerySet
from .utils import user_to_json


User = get_user_model()


def _validator():
    regex = RegexValidator(
        r"^[a-z]([a-z0-9_-]){0,62}[a-z0-9]$",
        message="由小写字母、数字、中横线、下划线组成，字母开头、字母或数据结尾，长度范围为2~64",
    )
    return regex


class BaseTimeModel(models.Model):

    class Meta:
        abstract = True

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("修改时间", auto_now=True)


class TreeNode(BaseTimeModel):

    TREE_SPECIAL_FIELDS = ("path", "depth", "node_hash", "updated_at")

    class Meta:
        app_label = "django_tree_perm"
        verbose_name = "树结点"
        ordering = ("path",)
        indexes = [
            models.Index(fields=["is_key", "disabled", "name"]),
        ]

    name = models.CharField(verbose_name="标识", max_length=64, db_index=True, validators=[_validator()])
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

    objects = TreeNodeManager.from_queryset(TreeNodeQuerySet)()

    def __str__(self):
        return f"TreeNode:{self.id} {self.path}"

    def to_json(self, partial=False):
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
                    "created_at": self.created_at.strftime(settings.TREE_DATETIME_FORMAT),
                    "updated_at": self.updated_at.strftime(settings.TREE_DATETIME_FORMAT),
                }
            )
        return data

    @property
    def path_prefix(self):
        return f"{self.path}{TREE_SPLIT_NODE_FLAG}"

    def get_self_and_children(self):
        qs = TreeNode.objects.filter(models.Q(path=self.path) | models.Q(path__startswith=self.path_prefix))
        return qs

    def _patch_attrs(self):
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

    def validate_save(self, **kwargs):
        self._patch_attrs()
        self.full_clean()
        self.save(**kwargs)


class Role(BaseTimeModel):

    class Meta:
        app_label = "django_tree_perm"
        verbose_name = "角色"

    name = models.CharField(
        verbose_name="唯一标识", max_length=64, db_index=True, unique=True, validators=[_validator()]
    )
    alias = models.CharField(verbose_name="显示名称", max_length=64, default="", blank=True)
    description = models.CharField(verbose_name="描述", max_length=1024, default="", blank=True)
    # 赋予该角色后，可以管理当前结点上的人员角色关系
    can_manage = models.BooleanField(verbose_name="允许管理结点", default=False)

    def to_json(self, partial=False, path=None):
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
                    "created_at": self.created_at.strftime(settings.TREE_DATETIME_FORMAT),
                    "updated_at": self.updated_at.strftime(settings.TREE_DATETIME_FORMAT),
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

    class Meta:
        app_label = "django_tree_perm"
        verbose_name = "结点角色关系"
        unique_together = ("node", "role", "user")

    node = models.ForeignKey(TreeNode, on_delete=models.CASCADE, related_name="noderole_set")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="noderole_set")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="noderole_set")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    def to_json(self, partial=False):
        data = {
            "id": self.id,
            "node_id": self.node_id,
            "role_id": self.role_id,
            "user_id": self.user_id,
            "created_at": self.created_at.strftime(settings.TREE_DATETIME_FORMAT),
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
