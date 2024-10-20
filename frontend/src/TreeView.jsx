import React, { useCallback, useEffect, useState, useRef } from 'react';
import PropTypes from 'prop-types';
import {
  PlusOutlined,
  SettingOutlined,
  ReloadOutlined,
  FormOutlined,
  DeleteOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { message, Tree, Input, Row, Col, Button, Modal, Form, Checkbox, Space, Dropdown, Tooltip, Spin } from 'antd';

import * as Enum from 'js-enumerate';

import SelectView from './restful-antd/components/SelectView';
import { useProtect } from './restful-antd/hooks';
import requests from './restful-antd/requests';
import {
  TreeApi,
  getPathParent,
  COMMON_FORM_COL_PROPS,
  COMMON_MODAL_PROPS,
  TREE_SPLIT_NODE_FLAG,
} from './tools';

const NodeMenu = new Enum([
  { key: 'REFRESH', value: 'refresh', label: '加载子结点' },
  { key: 'ADD', value: 'add', label: '新增子结点' },
  { key: 'EDIT', value: 'edit', label: '修改信息' },
  { key: 'DELETE', value: 'delete', label: '删除结点', danger: true },
]);

const NODE_MENU_ICON = {
  [NodeMenu.REFRESH]: <ReloadOutlined />,
  [NodeMenu.ADD]: <PlusOutlined />,
  [NodeMenu.EDIT]: <FormOutlined />,
  [NodeMenu.DELETE]: <DeleteOutlined />,
};

// 服务树作为关键key的字段
const TREE_KEY_FIELD = 'path';

const DEFALUT_DEPTH = 2;

/**
 * 从数结构数据中，根据path找到对应结点
 */
const findNodeByPath = (treeData, path) => {
  if (!path) {
    return null;
  }

  // 递归查找父类结点
  for (let i = 0; i < treeData.length; i++) {
    const node = treeData[i];
    if (path && node.path === path) {
      return node;
    }
    if (node.children) {
      if (path && node.path && path.startsWith(`${node.path}${TREE_SPLIT_NODE_FLAG}`)) {
        return findNodeByPath(node.children, path);
      }
    }
  }
  return null;
};

/**
 * 更新结点isLeaf属性，标记是否叶子结点，叶子结点无图标操作onLoad
 */
const refreshNodeLeaf = (treeData, isLoadAll = false) => {
  for (let i = 0; i < treeData.length; i++) {
    const node = treeData[i];
    if (node.is_key) {
      node.isLeaf = true;
    } else if (isLoadAll && !node.children?.length) {
      node.isLeaf = true;
    }
    if (node.children) {
      refreshNodeLeaf(node.children, isLoadAll);
    }
  }
};

/**
 * 向树结构数据treeData中，将nodes插入作为某结点的children
 */
const insertChildren = (treeData, nodes, parentPath) => {
  // 无任何子结点
  if (!nodes || nodes.length === 0) {
    return treeData;
  }
  // 更新结点isLeaf属性
  refreshNodeLeaf(nodes);
  // 若是刷新根结点
  if (!parentPath) {
    return nodes;
  }
  if (treeData.length === 0) {
    return nodes;
  }
  // 递归查找父类结点
  const parentNode = findNodeByPath(treeData, parentPath);
  // 未找到结果不做处理
  if (!parentNode) {
    return treeData;
  }
  parentNode.children = nodes;
  return treeData;
};

/**
 * 结点编辑后，树中寻找对应结点更新信息
 */
const refreshNodeInfo = (treeData, node) => {
  const curNode = findNodeByPath(treeData, node.path);
  if (curNode) {
    Object.assign(curNode, node);
  }
  return treeData;
};

/**
 * 根据父类path找到父类结点，将新增的结点插入到children中
 * @returns
 */
const nodeInsertChild = (treeData, parentPath, node) => {
  const parentNode = findNodeByPath(treeData, parentPath);
  if (!parentNode) {
    return treeData;
  }
  if (parentNode.children) {
    // 添加在最前面
    const keys = parentNode.children.map(item => item[TREE_KEY_FIELD]);
    if (!keys.includes(node[TREE_KEY_FIELD])) {
      parentNode.children.unshift(node);
    }
  } else {
    parentNode.children = [node];
  }
  return treeData;
};

/**
 * 树结构数据移除结点
 */
const nodeRemoveChild = (treeData, node) => {
  const parentPath = getPathParent(node.path);
  if (!parentPath) {
    return treeData.filter(item => item.id !== node.id);
  }
  const parentNode = findNodeByPath(treeData, parentPath);
  if (!parentNode || !parentNode.children) {
    return treeData;
  }
  parentNode.children = parentNode.children.filter(item => item[TREE_KEY_FIELD] !== node[TREE_KEY_FIELD]);
  return treeData;
};

// node展示信息
const getNodeLabel = node => {
  let label = node.alias ? `${node.name} (${node.alias})` : node.name;
  return label;
};

// 获取所有key
const genAllKeys = treeData => {
  let keys = [];
  for (let i = 0; i < treeData.length; i++) {
    const node = treeData[i];
    if (node.depth < 2) {
      keys.push(node[TREE_KEY_FIELD]);
    }
    if (node.children?.length > 0) {
      keys.push(node[TREE_KEY_FIELD]);
      keys = keys.concat(genAllKeys(node.children));
    }
  }
  return keys;
};

/**
 * 树展示组件
 */
const TreeView = ({ user, defaultValue, onChange }) => {
  const [protect] = useProtect();
  const [loading, setLoading] = useState(false);

  const treeRef = useRef();
  // 树结构数据
  const [treeData, setTreeData] = useState([]);
  const [selectedKey, setSelectedKey] = useState(defaultValue);
  // 展开的结点
  const [expandedKeys, setExpandedKeys] = useState([]);
  const [loadedKeys, setLoadedKeys] = useState([]);

  // 编辑类型
  const [editType, setEditType] = useState();
  const [editNode, setEditNode] = useState();
  // 编辑表单
  const [editModalVisiable, setEditModalVisiable] = useState(false);
  const [formRef] = Form.useForm();
  // 展开所有结点
  const [isExpanded, setExpanded] = useState(false);
  // 鼠标移动到的结点
  const [hoverNode, setHoverNode] = useState();
  // 搜索值
  const [searchValue, setSearchValue] = useState();
  const [searchCounter, setSearchCounter] = useState(0);

  const onTreeNodeSelect = useCallback(
    (key, node) => {
      if (key) {
        setSelectedKey(key);
        if (!node) {
          node = findNodeByPath(treeData, null, key);
        }
        if (typeof onChange === 'function') {
          onChange(node);
        }
      }
      // 不允许取消选择
    },
    [onChange, treeData],
  );

  // 根据结点刷新其子结点的数据
  const refreshByNode = useCallback(
    (node, callback) => {
      const params = {};
      if (node) {
        // eslint-disable-next-line camelcase
        params.parent_path = node.path;
      }
      requests
        .get(TreeApi.LAZY_LOAD, { params })
        .then(
          protect(resp => {
            const nodes = resp.data.results;
            setTreeData(oldData => {
              const values = insertChildren(oldData, nodes, node?.path);
              return [...values];
            });
            if (node) {
              // 刷新该结点后，默认展开展示
              setExpandedKeys(oldKeys => {
                // 过掉该结点下所有展开的子结点，使其可以再次触发onLoad
                const keys = oldKeys.filter(key => !key.startsWith(`${node[TREE_KEY_FIELD]}${TREE_SPLIT_NODE_FLAG}`));
                if (!keys.includes(node[TREE_KEY_FIELD])) {
                  keys.push(node[TREE_KEY_FIELD]);
                }
                return keys;
              });
              // 处理异步加载的key
              setLoadedKeys((oldKeys) => {
                const keys = oldKeys.filter(key => !key.startsWith(`${node[TREE_KEY_FIELD]}${TREE_SPLIT_NODE_FLAG}`));
                if (!keys.includes(node[TREE_KEY_FIELD])) {
                  keys.push(node[TREE_KEY_FIELD]);
                }
                return keys;
              });
            }
          }),
        )
        .finally(protect(() => callback && callback()));
    },
    [protect],
  );

  // 搜索结点 / 不传递参数时加载所有结点
  const fetchAllNode = useCallback(
    (params = null) => {
      setLoading(true);
      const isLoadAll = params ? false : true;
      requests
        .get(TreeApi.LOAD_ALL, { params })
        .then(
          protect(resp => {
            const nodes = resp.data.results;
            refreshNodeLeaf(nodes, isLoadAll);
            setTreeData(nodes);
            // 展开所有结点
            const keys = genAllKeys(nodes);
            setExpandedKeys(keys);
            if (!isLoadAll) {
              // 搜索过后重置异步加载的标记
              setLoadedKeys([]);
            }
          }),
        )
        .finally(protect(() => setLoading(false)));
    },
    [protect],
  );

  useEffect(() => {
    if (defaultValue && defaultValue.split(TREE_SPLIT_NODE_FLAG).length > DEFALUT_DEPTH) {
      // 有默认值，且结点深度超过设定值则按照搜索加载
      setSearchValue(defaultValue);
    } else {
      fetchAllNode({ depth: DEFALUT_DEPTH });
    }
    // 仅需在初始化时加载一次即可
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (searchValue === undefined || searchValue === null) {
      // 避免初始化的时候多次加载
      return;
    }
    setTimeout(() => {
      if (!searchValue) {
        fetchAllNode({ depth: DEFALUT_DEPTH });
      } else {
        fetchAllNode({ search: searchValue });
      }
    }, 200);
  }, [searchValue, searchCounter, fetchAllNode]);

  // 重置表单
  const resetFormData = useCallback(
    data => {
      const values = {
        name: null,
        alias: '',
        description: '',
        // eslint-disable-next-line camelcase
        parent_id: null,
        // eslint-disable-next-line camelcase
        is_key: false,
        ...data,
      };
      formRef?.setFieldsValue(values);
    },
    [formRef],
  );

  // 结点显示的样式
  const getNodeStyle = useCallback(
    node => {
      let style = {};
      if (node.is_key) {
        style.fontWeight = 'bold';
        style.color = '#fa8c16';
        if (searchValue && node.name.indexOf(searchValue) > -1) {
          style.color = '#fa541c';
        }
      }
      return style;
    },
    [searchValue],
  );

  // 结点可以操作的菜单列表
  const nodeUseMenus = useCallback(node => {
    const menus = NodeMenu.options
      .filter(menu => {
        if (node.is_key) {
          if ([NodeMenu.EDIT, NodeMenu.DELETE].includes(menu.value)) {
            return true;
          }
        } else {
          return true;
        }
        return false;
      })
      .map(item => ({ ...item, key: item.value, icon: NODE_MENU_ICON[item.value] }));
    return menus;
  }, []);

  // 弹窗消失时应当处理如下逻辑
  const onModalClose = useCallback(() => {
    setEditModalVisiable(false);
    setEditType(null);
    setEditNode(null);
    resetFormData();
  }, [resetFormData]);

  const onModealConfirm = useCallback(() => {
    formRef.validateFields().then(
      protect(values => {
        setLoading(true);
        if (editType === NodeMenu.EDIT) {
          requests
            .patch(TreeApi.nodeDetail(editNode.id), values)
            .then(
              protect(resp => {
                message.success('修改成功');
                onModalClose();
                const node = resp.data;
                // 通知信息变更
                onTreeNodeSelect(node[TREE_KEY_FIELD], node);
                // editNode 是当前操作要编辑的结点
                if (editNode.parent_id === node.parent_id) {
                  setTreeData(oldData => {
                    const data = refreshNodeInfo(oldData, node);
                    return [...data];
                  });
                } else {
                  // 改变了父类结点
                  fetchAllNode({ search: node.path });
                }
              }),
            )
            .finally(protect(() => setLoading(false)));
        } else {
          requests
            .post(TreeApi.NODE_LIST, values)
            .then(
              protect(resp => {
                message.success('新增成功');
                onModalClose();
                const node = resp.data;
                node.isLeaf = true;
                if (!node.parent_id) {
                  // 增加的是根结点
                  fetchAllNode({ depth: DEFALUT_DEPTH });
                } else if (editType === NodeMenu.ADD) {
                  // 新增的是子结点
                  if (editNode) {
                    // editNode 是父类结点
                    if (expandedKeys.includes(editNode[TREE_KEY_FIELD])) {
                      // 结点已经展开，直接插入数据
                      setTreeData(oldData => {
                        const data = nodeInsertChild(oldData, editNode.path, node);
                        return [...data];
                      });
                    } else {
                      // 未展开，直接刷新展开
                      refreshByNode(editNode);
                    }
                  }
                }
              }),
            )
            .finally(protect(() => setLoading(false)));
        }
      }),
      protect(() => {
        message.error('请正确填写表单');
      }),
    );
  }, [protect, formRef, editNode, editType, expandedKeys, onModalClose, refreshByNode, fetchAllNode, onTreeNodeSelect]);

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <Row gutter={10} wrap={false}>
        <Col flex="auto">
          <Input.Search
            defaultValue={defaultValue}
            placeholder="输入进行模糊搜索"
            loading={loading}
            onSearch={v => {
              setSearchValue(v);
              if (searchValue === v) {
                setSearchCounter(searchCounter + 1);
              }
            }}
            enterButton
          />
        </Col>
        <Col flex={user.tree_manager ? '120px' : '80px'}>
          <Space>
            <Tooltip title="加载全部结点">
              <Button
                type="primary"
                icon={<ReloadOutlined />}
                onClick={() => {
                  fetchAllNode();
                }}
              />
            </Tooltip>
            <Tooltip title="展开/收起已加载的节点">
              <Button
                type="primary"
                icon={<MenuUnfoldOutlined />}
                onClick={() => {
                  if (isExpanded) {
                    setExpandedKeys([]);
                  } else {
                    setExpandedKeys(genAllKeys(treeData));
                  }
                  setExpanded(v => !v);
                }}
              />
            </Tooltip>
            {
              user.tree_manager && (
                <Tooltip title="新增根结点">
                  <Button type="primary" icon={<PlusOutlined />} onClick={() => setEditModalVisiable(true)} />
                </Tooltip>
              )
            }
          </Space>
        </Col>
      </Row>
      <div className="cls-scoll-container cls-tree-view">
        <div className="cls-scoll-container-wrapper cls-tree-wrapper">
          <div className="cls-scoll-container-content">
            <Spin tip="加载中" spinning={loading}>
              <Tree

                ref={treeRef}
                treeData={treeData}
                fieldNames={{
                  title: 'name',
                  key: TREE_KEY_FIELD,
                }}
                titleRender={node => (
                  <Space
                    onMouseEnter={() => setHoverNode(node)}
                    onMouseLeave={() =>
                      setHoverNode(oldNode => {
                        if (oldNode[TREE_KEY_FIELD] === node[TREE_KEY_FIELD]) {
                          return null;
                        }
                        return oldNode;
                      })
                    }
                  >
                    <div id={`node-${node.path}`} style={getNodeStyle(node)}>{getNodeLabel(node)}</div>
                    <Dropdown
                      menu={{
                        items: nodeUseMenus(node),
                        onClick: menu => {
                          setEditType(menu.key);
                          switch (menu.key) {
                            case NodeMenu.REFRESH: {
                              refreshByNode(node);
                              break;
                            }
                            case NodeMenu.EDIT: {
                              setLoading(true);
                              requests
                                .get(TreeApi.nodeDetail(node.id))
                                .then(
                                  protect(resp => {
                                    setEditNode(node);
                                    setEditModalVisiable(true);
                                    resetFormData(resp.data);
                                  }),
                                )
                                .finally(protect(() => setLoading(false)));
                              break;
                            }
                            case NodeMenu.ADD: {
                              setEditNode(node);
                              setEditModalVisiable(true);
                              // eslint-disable-next-line camelcase
                              resetFormData({ parent_id: node.id });
                              break;
                            }
                            case NodeMenu.DELETE: {
                              Modal.warning({
                                title: '确认删除？',
                                content: (
                                  <div>
                                    <div>操作删除结点：{getNodeLabel(node)}</div>
                                    <div>结点路径: {node.path}</div>
                                  </div>
                                ),
                                destroyOnClose: true,
                                onOk: () => {
                                  requests.delete(TreeApi.nodeDetail(node.id), { params: { path: node.path } }).then(
                                    protect(() => {
                                      message.success(`删除 ${node.path} 成功`);
                                      setTreeData(oldData => {
                                        const data = nodeRemoveChild(oldData, node);
                                        return [...data];
                                      });
                                    }),
                                  );
                                },
                              });
                              break;
                            }
                            default:
                              break;
                          }
                        },
                      }}
                    >
                      <span
                        style={
                          hoverNode && hoverNode[TREE_KEY_FIELD] === node[TREE_KEY_FIELD] ? null : { display: 'none' }
                        }
                      >
                        <SettingOutlined style={{ padding: '0 5px' }} />
                      </span>
                    </Dropdown>
                  </Space>
                )}
                filterTreeNode={searchValue ? node => searchValue && node.name.indexOf(searchValue) > -1 : undefined}
                expandedKeys={expandedKeys}
                onExpand={(expandedKeys, { expanded, node }) => {
                  if (expanded && !loadedKeys.includes(node[TREE_KEY_FIELD])) {
                    refreshByNode(node);
                  } else {
                    setExpandedKeys(expandedKeys);
                  }
                }}
                loadedKeys={loadedKeys}
                onLoad={(loadedKeys => setLoadedKeys(loadedKeys))}
                loadData={node =>
                  new Promise(resolve => {
                    refreshByNode(node, resolve);
                  })
                }
                multiple={false}
                selectedKeys={selectedKey ? [selectedKey] : []}
                onSelect={(keys, { node }) => {
                  if (keys.length === 1) {
                    onTreeNodeSelect(keys[0], node);
                  } else {
                    onTreeNodeSelect(null, null);
                  }
                }}
              />
            </Spin>
          </div>
        </div>
      </div>
      <Modal
        title={NodeMenu.has(editType) ? NodeMenu.getLabel(editType) : '新增结点'}
        {...COMMON_MODAL_PROPS}
        confirmLoading={loading}
        open={editModalVisiable}
        onOk={() => onModealConfirm()}
        onCancel={() => onModalClose()}
      >
        <Form form={formRef} {...COMMON_FORM_COL_PROPS}>
          <Form.Item
            name="name"
            label="标识"
            rules={[
              {
                required: true,
                pattern: /^[a-z]([a-z0-9_-]){0,62}[a-z0-9]$/,
                message: '由小写字母、数字、中横线、下划线组成，字母开头、字母或数据结尾，长度范围为2~64',
              },
            ]}
          >
            <Input disabled={editType === NodeMenu.EDIT} count={{ show: true, max: 64 }}/>
          </Form.Item>
          <Form.Item
            name="alias"
            label="别名"
            rules={[
              {
                max: 64,
                message: '最多64个字符',
              },
            ]}
          >
            <Input count={{ show: true, max: 64 }}/>
          </Form.Item>
          <Form.Item
            name="description"
            label="描述"
            rules={[
              {
                max: 1024,
                message: '最多1024个字符',
              },
            ]}
          >
            <Input.TextArea autoSize={{ minRows: 3, maxRows: 6 }} count={{ show: true, max: 1024 }}/>
          </Form.Item>
          <Form.Item name="parent_id" label="父结点" help="无父类结点则新增的是根结点，更改则会影响其所有子结点">
            <SelectView
              disabled={editType === NodeMenu.ADD}
              restful={TreeApi.NODE_LIST}
              fieldNames={{ label: 'path', value: 'id' }}
            />
          </Form.Item>
          <Form.Item
            name="is_key"
            label="作为Key"
            valuePropName="checked"
          >
            <Checkbox disabled={editType === NodeMenu.EDIT} >勾选后该结点不允许新增叶子结点，且标识也是全局唯一</Checkbox>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

TreeView.propTypes = {
  user: PropTypes.object,
  // 传递树结点路径
  defaultValue: PropTypes.string,
  onChange: PropTypes.func,
};

export default TreeView;
