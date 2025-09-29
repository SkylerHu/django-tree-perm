# Self-Documented Makefile see https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: clean clean-build clean-dist clean-pyc lint test test-all coverage release dist install help
.DEFAULT_GOAL := help

VENV_NAME?=.env
PYTHON=${VENV_NAME}/bin/python

define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)


clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	find . -name '*.egg-info' -exec rm -fr {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -fr .coverage
	rm -fr .pytest_cache
	rm -fr htmlcov/

lint: ## check style with flake8
	pre-commit run -a

test: ## run tests quickly with the default Python
# 	${PYTHON} -m pip install --editable .  # 解决找不到Django配置的问题
	${PYTHON} -m pytest

test-all: lint ## run tests on every Python version with tox
	${PYTHON} -m tox

coverage: ## check code coverage quickly with the default Python
	${PYTHON} -m coverage run --source django_tree_perm -m pytest
	${PYTHON} -m coverage report -m
	${PYTHON} -m coverage html
	$(BROWSER) .coverage/htmlcov/index.html

release: clean-build ## package and upload a release
	${PYTHON} -m twine upload -r pypi dist/*(.whl|.tar.gz)

dist: clean-build ## builds source
	${PYTHON} setup.py sdist bdist_wheel
	ls -l dist
	${PYTHON} -m twine check dist/*(.whl|.tar.gz)

install: clean-build ## install the package to the active Python's site-packages
	${PYTHON} setup.py install

build-static: ## build frontend and copy to django_tree_perm static directory
	cd frontend && rm -rf build && npm run build && cd ..
	mkdir -p django_tree_perm/static/tree_perm
	rsync -avc --delete --exclude="*.map" --exclude="*.LICENSE.txt" --exclude="asset-manifest.json" frontend/build/ django_tree_perm/static/tree_perm/
	mv django_tree_perm/static/tree_perm/index.html django_tree_perm/templates/tree_perm/main.html
