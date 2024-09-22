#!/usr/bin/env python
# coding=utf-8
import bisect


TREE_SPLIT_NODE_FLAG = "."


def get_tree_paths(paths):
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
