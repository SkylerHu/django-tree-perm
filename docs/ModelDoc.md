# 数据库Model

## 1. TreeNode (树结点)

::: django_tree_perm.models.tree.TreeNode
    options:
        members:
            - TREE_SPECIAL_FIELDS
            - patch_attrs
            - validate_save
            - get_self_and_children
            - to_json
            - path_prefix

## 2. Role (角色)

::: django_tree_perm.models.tree.Role
    options:
        members:
            - to_json

## 3. NodeRole (结点/角色/用户关系)

::: django_tree_perm.models.tree.NodeRole
    options:
        members:
            - to_json

## 4. 其他

::: django_tree_perm.models.tree.tree_validator

::: django_tree_perm.models.manager.TreeNodeManager

::: django_tree_perm.models.manager.TreeNodeQuerySet
    options:
        members: true
