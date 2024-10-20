#!/usr/bin/env python
# coding=utf-8
import re

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from django_tree_perm import utils
from django_tree_perm import exceptions
from django_tree_perm.models import TreeNode, NodeRole


class TreeNodeManger(object):
    """
    树结点管理类
    """

    def __init__(self, node=None, user=None, **kwargs):
        """初始化

        Args:
            node: TreeNode, 结点对象
            user: User, 用户对象，传递该值后结点管理操作会校验权限
            kwargs: node传递None时通过该参数获取结点
        """
        if not node and kwargs:
            node = get_object_or_404(TreeNode, **kwargs)
        self.node = node
        self.user = user

    @classmethod
    def add_node(
        cls, name, alias="", description="", parent=None, parent_id=None, parent_path=None, is_key=False, user=None
    ):
        """新增树结点

        Args:
            name: str, 结点唯一标识
            alias: str, 别名. Defaults to "".
            description: str, 简介描述. Defaults to "".
            parent: TreeNode, 父类结点对象. Defaults to None.
            parent_id: int, 父结点ID. Defaults to None.
            parent_path: str, 父结点路径. Defaults to None.
            is_key: bool, 是否作为Key, 为True时唯一标识name全局唯一. Defaults to False.
            user: User, 操作用户对象. Defaults to None.

        Raises:
            exceptions.PermDenyException: 无权限时抛出的异常
            exceptions.ParamsValidateException: 结点数据校验异常

        Returns:
            管理类实例化
        """
        if not name:
            raise exceptions.ParamsValidateException("Node name cannot be empty.")
        if utils.TREE_SPLIT_NODE_FLAG in name:
            raise exceptions.ParamsValidateException(
                f"Node name is not allowed to contain separator [{utils.TREE_SPLIT_NODE_FLAG}]"
            )

        parent = cls.find_parent_node(parent=parent, parent_id=parent_id, parent_path=parent_path)

        # 校验权限
        if user:
            if not parent and not PermManager.has_tree_perm(user):
                raise exceptions.PermDenyException("Only superuser can add a new root node")
            if parent and not PermManager.has_node_perm(user, path=parent.path, can_manage=True):
                raise exceptions.PermDenyException(f"No add permission for the parent path={parent.path}")

        if is_key and not parent:
            # 叶子结点不允许是根结点
            raise exceptions.ParamsValidateException("Leaf nodes are not allowed to be root node.")
        values = {
            "name": name,
            "alias": alias or "",
            "description": description or "",
            "parent": parent,
            "is_key": is_key,
            "disabled": False,
        }
        node = TreeNode(**values)
        node.validate_save()
        return cls(node=node, user=user)

    @transaction.atomic
    def update_attrs(self, name=None, alias=None, description=None, parent_id=None):
        """更新结点信息，参数不传递则表示不更新

        Args:
            name: str, 唯一标识. Defaults to None.
            alias: str, 别名. Defaults to None.
            description: str, 简介. Defaults to None.
            parent_id: int, 父类结点ID. Defaults to None.

        Raises:
            exceptions.PermDenyException: 无权限时抛出的异常
            exceptions.ParamsValidateException: 结点数据校验异常
        """
        node = self.node
        # 校验权限
        if self.user and not PermManager.has_node_perm(self.user, path=node.path, can_manage=True):
            raise exceptions.PermDenyException(f"No update permission for the path={node.path}")

        is_change = False
        if name and node.name != name:
            if node.is_key:
                raise exceptions.ParamsValidateException("The key node does not allow edit name.")
            if utils.TREE_SPLIT_NODE_FLAG in name:
                raise exceptions.ParamsValidateException(
                    f"Node name is not allowed to contain separator [{utils.TREE_SPLIT_NODE_FLAG}]"
                )
            is_change = True
            node.name = name
        if alias is not None and node.alias != alias:
            is_change = True
            node.alias = alias
        if description is not None and node.description != description:
            is_change = True
            node.description = description

        if is_change:
            node.validate_save()

        if parent_id and node.parent_id != parent_id:
            self.move_path(parent_id=parent_id)

    @transaction.atomic
    def move_path(self, parent=None, parent_id=None, parent_path=None):
        """更改结点的父类结点（即移动结点在树结构中的位置）

        - 会更新该结点下所有子结点的信息，主要是更新结点path属性；
        - 暂不允许将结点转为根结点，parent、parent_id、parent_path参数必须有一个;
        - 可用于恢复 disabled=True 的结点

        Args:
            parent: TreeNode, 父类结点. Defaults to None.
            parent_id: int, 父类结点ID. Defaults to None.
            parent_path: str, 父类结点路径. Defaults to None.

        Raises:
            exceptions.PermDenyException: 无权限时抛出的异常
            exceptions.ParamsValidateException: 结点数据校验异常

        Returns:
            更新结点记录数量
        """
        parent = self.find_parent_node(parent=parent, parent_id=parent_id, parent_path=parent_path, required=True)
        node = self.node
        # 校验权限
        if self.user and not PermManager.has_node_perm(self.user, path=node.path, can_manage=True):
            raise exceptions.PermDenyException(f"No move permission for the path={parent.path}")
        if self.user and parent:
            if not PermManager.has_node_perm(self.user, path=parent.path, can_manage=True):
                raise exceptions.PermDenyException(f"No move permission for the parent path={parent.path}")

        if node.path == parent.path or parent.path.startswith(node.path_prefix):
            # 不能选择自己以及自身的子结点
            raise exceptions.ParamsValidateException("Cannot be its own child node.")
        if node.parent_id == parent.id:
            # 已在节点下无需处理
            return 0

        node.parent = parent
        node.disabled = False
        # 要更新所有子结点path属性
        old_prefix = node.path_prefix  # 提前记录旧的树路径
        # 优先更新结点自身
        node.validate_save()
        rows = 1

        # 更新所有子结点path属性
        nodes = list(TreeNode.objects.filter(path__startswith=old_prefix))
        if nodes:
            new_prefix = node.path_prefix
            for _node in nodes:
                re_prefix = old_prefix.replace(".", "\\.")
                _node.path = re.sub(rf"^{re_prefix}", new_prefix, _node.path, flags=0)
                _node._patch_attrs()
            TreeNode.objects.bulk_update(nodes, TreeNode.TREE_SPECIAL_FIELDS, batch_size=1000)
            rows += len(nodes)
        return rows

    @transaction.atomic
    def remove(self, clear_chidren=False):
        """删除结点

        - 普通结点，直接删除数据库记录；
        - is_key=True 的结点，不允许删除数据库记录，删除操作仅将 disabled 置为 True

        Args:
            clear_chidren: bool, 是否允许连带删除所有子结点. Defaults to False, 此时若有子结点不允许被删除.

        Raises:
            exceptions.PermDenyException: 无权限时抛出的异常
            exceptions.ParamsValidateException: 结点数据校验异常

        Returns:
            删除结点数据库记录的数量
        """
        node = self.node
        # 校验权限
        if self.user and not PermManager.has_node_perm(self.user, path=node.path, can_manage=True):
            raise exceptions.PermDenyException(f"No remove permission for the path={node.path}")

        if node.is_key and node.disabled:
            raise exceptions.ParamsValidateException("The node has been disabled. Repeated operation is not allowed.")

        if node.is_key:
            node.parent = None
            node.disabled = True
            node.validate_save()
            # 清除结点相关用户权限
            NodeRole.objects.filter(node_id=node.id).delete()
            return 0

        has_children = node.children.exists()
        if has_children and not clear_chidren:
            # 若是有子结点不允许直接删除
            raise exceptions.ParamsValidateException(
                "Deleting nodes that have child nodes is not allowed. Please pass parameter 'clear_chidren=True'"
            )

        if not has_children:
            # 会级联删除相关用户权限
            node.delete()
            return 1
        # 处理子结点
        query_set = node.get_self_and_children()
        # 更新所有叶子key结点为disabled
        node_ids = []
        nodes = []
        for _node in query_set.filter(is_key=True, disabled=False):
            _node.disabled = True
            _node.parent = None
            _node._patch_attrs()
            nodes.append(_node)
            node_ids.append(_node.id)
        if nodes:
            fields = list(set(["disabled", "parent"] + list(TreeNode.TREE_SPECIAL_FIELDS)))
            TreeNode.objects.bulk_update(nodes, fields, batch_size=1000)
            # 清除结点相关用户权限
            NodeRole.objects.filter(node_id__in=node_ids).delete()
        # 删除所有子结点
        row, _ = query_set.filter(is_key=False).delete()
        return row

    @classmethod
    def find_parent_node(cls, parent=None, parent_id=None, parent_path=None, required=False):
        """根据参初始化父类结点，并判断结点是否能够作为父类结点

        Args:
            parent: TreeNode, 父类结点. Defaults to None.
            parent_id: int, 父类结点ID. Defaults to None.
            parent_path: str, 父类结点路径. Defaults to None.
            required: bool, 初始化后父类结点是否允许为空. Defaults to False.

        Raises:
            exceptions.PermDenyException: 无权限时抛出的异常
            exceptions.ParamsValidateException: 结点数据校验异常

        Returns:
            父类结点对象，可为空
        """
        parent = cls.get_node_object(node=parent, node_id=parent_id, path=parent_path, required=required)
        if parent:
            if parent.is_key:
                raise exceptions.ParamsValidateException("This key node is not allowed to be a parent node.")
        return parent

    @classmethod
    def get_node_object(cls, node=None, node_id=None, key_name=None, path=None, required=False):
        """获取结点对象

        Args:
            node: TreeNode, 结点对象. Defaults to None.
            node_id: int, 结点ID. Defaults to None.
            key_name: str，is_key=True情况下的结点唯一标识. Defaults to None.
            path: str, 结点路径. Defaults to None.
            required: bool, 初始化后父类结点是否允许为空. Defaults to False.

        Raises:
            exceptions.PermDenyException: 无权限时抛出的异常
            exceptions.ParamsValidateException: 结点数据校验异常

        Returns:
            结点对象，可为空
        """
        try:
            if node and not isinstance(node, TreeNode):
                raise exceptions.ParamsValidateException("must be a TreeNode instance.")
            if not node and key_name:
                node = TreeNode.objects.get(name=key_name, is_key=True)
            if not node and node_id:
                node = TreeNode.objects.get(id=node_id)
            if not node and path:
                node = TreeNode.objects.get(path=path)
        except ObjectDoesNotExist:
            pass

        if node:
            if node.disabled:
                raise exceptions.ParamsValidateException("This node is disabled.")
        elif required:
            raise exceptions.ParamsValidateException("This node not found, and cannot be null.")
        return node

    @classmethod
    def load_tree_data(cls, data):
        """加载JSON树结构数据写入数据库中

        Args:
            data: list 树结构数据

        Returns:
            int 新增结点个数
        """

        def _save_nodes(items, parent=None):
            count = 0
            for item in items:
                # 提取子结点数据
                children = item.pop("children", [])
                name = item["name"]
                # 处理当前结点
                path = utils.TREE_SPLIT_NODE_FLAG.join([parent.path, name]) if parent else name
                node = TreeNode.objects.filter(path=path).first()
                if not node:
                    count += 1
                    node = TreeNode(parent_id=parent.id if parent else None, **item)
                    node.validate_save()
                # 处理子结点
                count += _save_nodes(children, parent=node)
            return count

        with transaction.atomic():
            total = _save_nodes(data)

        return total

    @classmethod
    def to_json_tree(cls, queryset, trace_to_root=True):
        """将查询的结点对象，转换成树型结构json数据；需追溯到根结点用于树型结构展示

        Args:
            queryset: QuerySet[TreeNode], 结点查询条件
            trace_to_root: bool, 追溯到根结点数据. Defaults to True.

        Returns:
            list[dict] 树型结构json数据
        """
        if trace_to_root:
            paths = utils.get_tree_paths(list(queryset.values_list("path", flat=True)))
            queryset = TreeNode.objects.all().filter(path__in=paths)

        tree = []
        # 以parent_id为key, value是数组--存放直接子结点
        parent_child_nodes = {}
        for node in queryset:
            if node.parent_id:
                parent_child_nodes.setdefault(node.parent_id, [])
                parent_child_nodes[node.parent_id].append(node.to_json(partial=True))
            else:
                tree.append(node.to_json(partial=True))

        # 组装树形结构
        leafs = tree
        while True:
            if not leafs:
                break
            new_leafs = []
            for parent in leafs:
                children = parent_child_nodes.get(parent["id"], [])
                if children:
                    parent["children"] = children
                    new_leafs.extend(children)
            leafs = new_leafs

        return tree


class PermManager(object):
    """权限管理"""

    @classmethod
    def has_tree_perm(cls, user):
        """判断是否有树的管理权限; 仅 is_active 且 is_superuser 用户有关联权限

        - 操作新增根结点；
        - 对所有结点增删改查；
        - 对角色进行增删改查；

        Args:
            user: User, 用户

        Returns:
            bool, 有无权限
        """
        if user and user.is_active and user.is_superuser:
            return True
        return False

    @classmethod
    def has_node_perm(cls, user, path=None, key_name=None, roles=None, can_manage=False):
        """是否有某个结点的权限

        - 主要用于其他系统调用，判断用户是否有某key node的权限；
        - 结点的管理权限判断，需传递参数 can_manage=True；

        Args:
            user: User, 用户
            path: str, 结点路径
            key_name: str, key结点的标识
            roles: list[str], 有限定角色的权限，有任意其中一种角色便是有权限. Defaults to None, 不传递表示系统中任意角色都可行.
            can_manage: 是否有管理结点的权限. Defaults to False.

        Returns:
            bool, 有无权限
        """
        if cls.has_tree_perm(user):
            # 有树结点权限，则所有结点均有权限
            return True

        if not user:
            return False

        node = None
        if key_name:
            node = TreeNode.objects.filter(is_key=True, name=key_name).first()
        elif path:
            node = TreeNode.objects.filter(path=path).first()
        if not node or node.disabled:
            return False

        paths = utils.get_tree_paths(node.path)
        # 判断是否有权限
        queryset = NodeRole.objects.filter(user_id=user.id, node__path__in=paths)
        if roles:
            queryset = queryset.filter(role__name__in=roles)
        if can_manage:
            queryset = queryset.filter(role__can_manage=True)
        # 存在记录则有权限
        return queryset.exists()
