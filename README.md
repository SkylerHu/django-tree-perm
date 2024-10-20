# django-tree-perm

[![PyPI - Version](https://img.shields.io/pypi/v/django-tree-perm)](https://github.com/SkylerHu/django-tree-perm)
[![GitHub Actions Workflow Status](https://github.com/SkylerHu/django-tree-perm/actions/workflows/pre-commit.yml/badge.svg?branch=master)](https://github.com/SkylerHu/django-tree-perm)
[![GitHub Actions Workflow Status](https://github.com/SkylerHu/django-tree-perm/actions/workflows/test-py3.yml/badge.svg?branch=master)](https://github.com/SkylerHu/django-tree-perm)
[![Coveralls](https://img.shields.io/coverallsCoverage/github/SkylerHu/django-tree-perm?branch=master)](https://github.com/SkylerHu/django-tree-perm)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/django-tree-perm)](https://github.com/SkylerHu/django-tree-perm)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-tree-perm)](https://github.com/SkylerHu/django-tree-perm)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/django-tree-perm)](https://github.com/SkylerHu/django-tree-perm)
[![GitHub License](https://img.shields.io/github/license/SkylerHu/django-tree-perm)](https://github.com/SkylerHu/django-tree-perm)
[![Read the Docs](https://img.shields.io/readthedocs/django-tree-perm)](https://django-tree-perm.readthedocs.io)


django-tree-perm is implemented by Django and provides interfaces and pages for managing tree data structure nodes.

django-tree-perm 是 Django 实现的，提供了树形数据结构结点管理的接口和页面。

主要应用场景有：
- CMDB服务树的管理；
- web项目页面权限的管理控制；

## 1. 安装

	pip install django-tree-perm

可查看版本变更记录 [ChangeLog](./docs/CHANGELOG-1.x.md)

## 2. 使用
在项目 `settings.py` 中配置引入：

```python
INSTALLED_APPS = [
    # ...
    "django_tree_perm",
]
```

在项目 `urls.py` 中加入接口配置：
```python
path("tree/", include("django_tree_perm.urls")),
```

执行数据库变更：
```shell
python manage.py migrate django_tree_perm
```

运行服务： `python manage.py runserver 0.0.0.0:8000`

可通过浏览器访问展示及管理页面 `http://localhost:8000/tree/`

## 3. 介绍
具体使用说明可以查看 [readthedocs](https://django-tree-perm.readthedocs.io) 或者直接查看源码注释。

## 4. Demo示例
![](./docs/statics/demo.gif)
