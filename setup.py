#!/usr/bin/env python
# coding=utf-8
import re

from setuptools import setup, find_packages


def read(file_name: str) -> str:
    with open(file_name, "r") as f:
        content = f.read()
    return content


version = re.search("__version__ = ['\"]([^'\"]+)['\"]", read("django_tree_perm/__init__.py")).group(1)  # type: ignore

read_me = read("README.md")
# 替换文档的相对路径为绝对路径地址
read_me = read_me.replace("(./docs/", "(https://github.com/SkylerHu/django-tree-perm/blob/master/docs/")


setup(
    name="django-tree-perm",
    version=version,
    url="https://github.com/SkylerHu/django-tree-perm.git",
    author="SkylerHu",
    author_email="skylerhu@qq.com",
    description="python tools",
    keywords=["cmdb", "tree", "tree-permission"],
    long_description=read_me,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*", "tests", "example_project"]),
    license="MIT Licence",
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=[
        "py-enum>=1.1.1",
        "django>=3.0",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
