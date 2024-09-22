#!/usr/bin/env python
# coding=utf-8
import hashlib

from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model

from django_tree_perm import settings
from django_tree_perm.utils import TREE_SPLIT_NODE_FLAG
from .manager import TreeNodeManager


User = get_user_model()


def _validator():
    regex = RegexValidator(
        r"^[a-b][a-b0-9_-]{1,63}$", message="字母开头, 由小写字母、数字、中横线、下划线组成，长度范围为2~64个字符"
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

    name = models.CharField(verbose_name="唯一标识", max_length=64, db_index=True, validators=[_validator()])
    alias = models.CharField(verbose_name="显示名称", max_length=128, default="")
    description = models.CharField(verbose_name="描述", max_length=1024, default="")
    # 父类结点为空时，表示是树的根结点
    parent = models.ForeignKey(
        "self",
        verbose_name="父类结点",
        related_name="children",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    # is_key=True的结点不允许新增子结点
    is_key = models.BooleanField(verbose_name="绝对叶子结点", default=False)
    # 叶子结点不可以删除，仅用于叶子结点
    disabled = models.BooleanField(verbose_name="是否禁用", default=False, db_index=True)
    # 以下字段不允许直接赋值更新
    path = models.CharField(verbose_name="结点全路径", max_length=191, default="", db_index=True)
    # 树的根结点深度为1
    depth = models.SmallIntegerField(verbose_name="深度", default=1)
    # 为了保证叶子结点name全局唯一，且有些数据库例如mysql不支持 UniqueConstraint按照条件约束
    node_hash = models.CharField(verbose_name="结点哈希值", unique=True, max_length=32, db_index=True)

    objects = TreeNodeManager()

    def __str__(self):
        return f"TreeNode:{self.id} {self.path}"

    def to_json(self):
        data = {
            "id": self.id,
            "name": self.name,
            "alias": self.alias,
            "description": self.description,
            "parent_id": self.parent_id,
            "is_key": self.is_key,
            "disabled": self.disabled,
            "path": self.path,
            "depth": self.depth,
            "created_at": self.created_at.strftime(settings.DATETIME_FORMAT),
            "updated_at": self.updated_at.strftime(settings.DATETIME_FORMAT),
        }
        return data

    @property
    def path_prefix(self):
        return f"{self.path}{TREE_SPLIT_NODE_FLAG}"

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

    def save(self, update_fields=None, **kwargs):
        self._patch_attrs()
        if update_fields:
            update_fields = list(set(update_fields) + set(self.TREE_SPECIAL_FIELDS))
        super().save(update_fields=update_fields, **kwargs)


class PermRole(BaseTimeModel):

    class Meta:
        app_label = "django_tree_perm"
        verbose_name = "角色"

    name = models.CharField(
        verbose_name="唯一标识", max_length=64, db_index=True, unique=True, validators=[_validator()]
    )
    alias = models.CharField(verbose_name="显示名称", max_length=128, default="")
    description = models.CharField(verbose_name="描述", max_length=1024, default="")
    # 赋予该角色后，可以管理当前结点上的人员角色关系
    can_manage = models.BooleanField(verbose_name="是否管理员", default=False)


class NodeRole(models.Model):

    class Meta:
        app_label = "django_tree_perm"
        verbose_name = "结点角色关系"
        unique_together = ("node", "role", "user")

    node = models.ForeignKey(TreeNode, on_delete=models.CASCADE, related_name="noderole_set")
    role = models.ForeignKey(PermRole, on_delete=models.CASCADE, related_name="noderole_set")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="noderole_set")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
