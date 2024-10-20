#!/usr/bin/env python
# coding=utf-8
import bisect


# 结点层级分隔符
TREE_SPLIT_NODE_FLAG = "."

# 接口读方法
SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


def get_tree_paths(paths):
    """根据path获取所有父类路径

    例如 "a.b.c" 返回 ["a", "a.b", "a.b.c"]

    Args:
        paths: str or list[str], 输入树结点路径

    Returns:
        list，返回路径及其所有父类路径
    """
    if not paths:
        return []

    if isinstance(paths, str):
        paths = [paths]

    results = []
    for _path in paths:
        path = None
        for name in _path.split(TREE_SPLIT_NODE_FLAG):
            if path is None:
                path = name
            else:
                path = TREE_SPLIT_NODE_FLAG.join([path, name])
            if path not in results:
                # 不存在则按顺序插入数组中
                bisect.insort_right(results, path)
    return results


def get_path_parent(path):
    """获取树结点路径的直接父类路径

    Args:
        path: str 树结点路径，eg: a.b.c

    Returns:
        str, 直接父类路径，eg: a.b
    """
    if not path:
        return ""
    info = path.split(TREE_SPLIT_NODE_FLAG)
    if len(info) <= 1:
        return ""
    return TREE_SPLIT_NODE_FLAG.join(info[:-1])
