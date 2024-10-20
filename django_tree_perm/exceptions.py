#!/usr/bin/env python
# coding=utf-8


class TreeBaseException(Exception):
    """内部异常基类"""

    pass


class ParamsValidateException(TreeBaseException):
    """参数校验异常"""

    pass


class PermDenyException(TreeBaseException):
    """无权限操作异常"""

    pass
