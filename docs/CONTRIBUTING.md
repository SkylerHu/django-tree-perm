# 前言
主要是给开发者阅读，描述开发前后需要注意的一些事项。

# 开发环境
- `python3.9`的python环境
- 新建虚拟环境`.env`在项目根目录下，`source .env/bin/activate`
    - python3.9 -m venv .env
- `pip install -r requirements_dev.txt`
- 系统安装`brew install pre-commit` 或者 `pip install pre-commit`
    - brew安装`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"`
    - 在项目更目录下执行`pre-commit install --hook-type pre-commit --hook-type commit-msg`
- 可通过`pip install -e ./`编辑模式安装用于边开发边测试使用

# 项目部分结构说明
- `pytest.ini` 测试脚本的配置
- `.coveragerc` 测试覆盖度工具使用的配置，在pytest.ini中引用
- `.pre-commit-config.yaml` git提交代码前pre-commit执行的检测相关配置
- `requirements_dev.txt` 开发需要的环境
- `requirements_test.txt` 跑测试用例需要的环境
- `tests` 测试用例目录
    - `conftest.py` pytest测试用例全局变量配置
    - `settings` Django settings配置，在pytest.ini中引用
- `django_tree_perm` lib核心代码
    - static `注意` 文件通过在外层根目录下执行 `make build-static` 由 frontend 项目代码构建生成
    - templates
- `example_project` 开发测试的demo项目
- `frontend` 配套的前端管理项目
- `MANIFEST.in` 打包相关-清单文件配置
- `Makefile` 构建配置，可以执行`make help`查看具体命令
    - 定义了测试、打包、发版等很多命令
- `tox.ini` 定义各种Python版本的测试

# 提交Pull Request
提交Pull Request之前需要检查以下事项是否完成：
- 需包含测试用例，并通过`make test-all`
- 测试覆盖度要求 `make coverage`
- 尝试本地打包 `make dist`

# 运行测试用例

    pytest tests
    # 运行所有环境的测试用例
    tox run

# 文档
```shell
mkdocs build --clean  # 生成site文档网站
mkdocs serve  # 可以启动本地访问文档
```

文档发布未集成自动化，需要在 [https://readthedocs.org/](https://readthedocs.org/) 操作导入/生成新的文档。

# 打包发版

（以下命令都定义在了Makefile中了）

- `make clean-build` 删除本地构建缓存目录：`*_tools.egg-info`和`dist`
- `make build-static` 重新生成 `django_tree_perm/static` 中的静态文件
- `python setup.py sdist bdist_wheel` 执行打包
- `twine check dist/py*(.whl|.tar.gz)` 检查生成的文件是否符合pypi的要求
- `twine upload -r pypi dist/py*(.whl|.tar.gz)` 上传包
    - 需要本地`~/.pypirc`配置用户名密码
