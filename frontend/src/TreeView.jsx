import React, { useCallback, useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { PlusOutlined, SettingOutlined, ReloadOutlined, FormOutlined, DeleteOutlined, MenuUnfoldOutlined } from '@ant-design/icons';
import { message, Tree, Input, Row, Col, Button, Modal, Form, Checkbox, Space, Dropdown, Tooltip } from 'antd';

import * as Enum from 'js-enumerate';

import SelectView from './restful-antd/components/SelectView';
import { useProtect } from './restful-antd/hooks';
import requests, { formatRequestError } from './restful-antd/requests';
import { TreeApi } from './constants';

const NodeMenu = new Enum([
  { key: 'REFRESH', value: 'refresh', label: '刷新子结点' },
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

const TREE_KEY_FIELD = 'id';

const findNodeByPath = (treeData, path) => {
  if (!path) {
    return null;
  }
  // 递归查找父类结点
  for (let i = 0; i < treeData.length; i++) {
    const node = treeData[i];
    if (node.path === path) {
      return node;
    }
    if (node.path && path.startsWith(node.path) && node.children) {
      return findNodeByPath(node.children, path);
    }
  }
  return null;
};

/**
 * 向树结构数据treeData中，将nodes插入作为某结点的chi˜ldren
 */
const insertChildren = (treeData, nodes, parent_path) => {
  // 无任何子结点
  if (!nodes || nodes.length === 0) {
    return treeData;
  }
  // 更新结点isLeaf属性
  nodes.forEach(node => {
    if (node.is_key) {
      node.isLeaf = node.is_key;
    }
  });
  // 若是刷新根结点
  if (!parent_path) {
    return nodes;
  }
  if (treeData.length === 0) {
    return nodes;
  }
  // 递归查找父类结点
  const parentNode = findNodeByPath(treeData, parent_path);
  // 未找到结果不做处理
  if (!parentNode) {
    return treeData;
  }
  parentNode.children = nodes;
  return treeData;
};

// 更新结点信息
const refreshNodeInfo = (treeData, node) => {
  const curNode = findNodeByPath(treeData, node.path);
  if (curNode) {
    Object.assign(curNode, node);
  }
  return treeData;
};

// 插入子结点
const nodeInsertChild = (treeData, parent_path, node) => {
  const parentNode = findNodeByPath(treeData, parent_path);
  if (!parentNode) {
    return treeData;
  }
  if (parentNode.children) {
    // 添加在最前面
    const keys = parentNode.children.map(node => node[TREE_KEY_FIELD]);
    if (!keys.includes(node[TREE_KEY_FIELD])) {
      parentNode.children.unshift(node);
    }
  } else {
    parentNode.children = [node];
  }
  return treeData;
};

// 获取所有key
const genAllKeys = (treeData) => {
  let keys = treeData.map(node => node[TREE_KEY_FIELD]);
  for (let i = 0; i < treeData.length; i++) {
    const node = treeData[i];
    if (node.children) {
      keys = keys.concat(genAllKeys(node.children));
    }
  }
  return keys;
};

const TreeView = () => {
  const [protect] = useProtect();
  const [loading, setLoading] = useState(false);
  // 编辑表单
  const [editModalVisiable, setEditModalVisiable] = useState(false);
  const [formRef] = Form.useForm();
  // 编辑类型
  const [editType, setEditType] = useState();
  const [editNode, setEditNode] = useState();
  // 树结构数据
  const [treeData, setTreeData] = useState([]);
  // 展开的结点
  const [expandedKeys, setExpandedKeys] = useState([]);
  // 鼠标移动到的结点
  const [hoverNode, setHoverNode] = useState();

  // 根据结点刷新其子结点的数据
  const refreshByNode = useCallback(
    (node, callback) => {
      const params = {};
      if (node) {
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
                if (oldKeys.includes(node[TREE_KEY_FIELD])) {
                  return oldKeys;
                }
                return oldKeys.concat([node[TREE_KEY_FIELD]]);
              });
            }
          }),
        )
        .finally(protect(() => callback && callback()));
    },
    [protect],
  );

  useEffect(() => {
    // refreshByNode();
    requests.get(TreeApi.LOAD_ALL, { params: { depth: 2 } }).then(
      protect(resp => {
        const nodes = resp.data.results;
        setTreeData(nodes);
        setExpandedKeys(nodes.map(node => node[TREE_KEY_FIELD]));
      }),
    );
    // 仅需在初始化时加载一次即可
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 重置表单
  const resetFormData = useCallback(
    data => {
      const values = {
        name: null,
        alias: '',
        description: '',
        parent_id: null,
        is_key: false,
        ...data,
      };
      formRef?.setFieldsValue(values);
    },
    [formRef],
  );

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
                setTreeData(oldData => {
                  const data = refreshNodeInfo(oldData, resp.data);
                  return [...data];
                });
              }),
            )
            .finally(protect(() => setLoading(false)));
        } else {
          requests
            .post(TreeApi.NODE_LIST, values)
            .then(
              protect(resp => {
                message.success('操作成功');
                onModalClose();
                if (editNode) {
                  if (expandedKeys.includes(editNode[TREE_KEY_FIELD])) {
                    // 结点已经展开，直接插入数据
                    const node = resp.data;
                    node.isLeaf = true;
                    setTreeData(oldData => {
                      const data = nodeInsertChild(oldData, editNode.path, node);
                      return [...data];
                    });
                  } else {
                    // 未展开，直接刷新展开
                    refreshByNode(editNode);
                  }
                }
              }),
              protect(error => {
                const { err_msg } = formatRequestError(error);
                message.error(`操作失败，请重试. ${err_msg}`);
              }),
            )
            .finally(protect(() => setLoading(false)));
        }
      }),
      protect(() => {
        message.error('请正确填写表单');
      }),
    );
  }, [formRef, editNode, editType, protect, onModalClose, refreshByNode, expandedKeys]);

  return (
    <div style={{ width: '100%', height: '100%', padding: 10 }}>
      <Row gutter={10}>
        <Col span={20}>
          <Input.Search
            styles={{ width: '100%' }}
            placeholder="输入关键字进行搜索"
            // onSearch={value => {}}
            enterButton
          />
        </Col>
        <Col span={4}>
          <Space>
            <Tooltip title="加载全部结点">
              <Button
                type="primary"
                icon={<ReloadOutlined />}
                onClick={() => {
                  requests.get(TreeApi.LOAD_ALL).then(
                    protect(resp => {
                      const nodes = resp.data.results;
                      setTreeData(nodes);
                      setExpandedKeys(nodes.map(node => node[TREE_KEY_FIELD]));
                    }),
                  );
                }}
              />
            </Tooltip>
            <Tooltip title="展开/折叠所有节点">
              <Button type="primary" icon={<MenuUnfoldOutlined />} onClick={() => {
                if (expandedKeys.length > 0) {
                  setExpandedKeys([]);
                } else {
                  setExpandedKeys(genAllKeys(treeData));
                }
              }} />
            </Tooltip>
            <Tooltip title="新增根结点">
              <Button type="primary" icon={<PlusOutlined />} onClick={() => setEditModalVisiable(true)} />
            </Tooltip>
          </Space>
        </Col>
      </Row>
      <div style={{ height: 10 }} />
      <Tree
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
            <div>{node.alias ? `${node.name} (${node.alias})` : node.name}</div>
            <Dropdown
              menu={{
                items: NodeMenu.options.map(item => ({ ...item, key: item.value, icon: NODE_MENU_ICON[item.value] })),
                onClick: menu => {
                  setEditType(menu.key);
                  switch (menu.key) {
                    case NodeMenu.REFRESH: {
                      refreshByNode(node);
                      break;
                    }
                    case NodeMenu.EDIT: {
                      setEditNode(node);
                      setEditModalVisiable(true);
                      resetFormData(node);
                      break;
                    }
                    case NodeMenu.ADD: {
                      setEditNode(node);
                      setEditModalVisiable(true);
                      resetFormData({ parent_id: node.id });
                      break;
                    }
                    case NodeMenu.DELETE: {
                      break;
                    }
                    default:
                      break;
                  }
                },
              }}
            >
              <SettingOutlined style={hoverNode && hoverNode[TREE_KEY_FIELD] === node[TREE_KEY_FIELD] ? null : { display: 'none' }}/>
            </Dropdown>
          </Space>
        )}
        expandedKeys={expandedKeys}
        onExpand={expandedKeys => setExpandedKeys(expandedKeys)}
        loadData={node =>
          new Promise(resolve => {
            refreshByNode(node, resolve);
          })
        }
      />
      <Modal
        title={NodeMenu.has(editType) ? NodeMenu.getLabel(editType) : '新增结点'}
        width="50%"
        maskClosable={false}
        destroyOnClose
        confirmLoading={loading}
        open={editModalVisiable}
        onOk={() => onModealConfirm()}
        onCancel={() => onModalClose()}
      >
        <Form form={formRef} labelCol={{ flex: '120px' }} wrapperCol={{ xs: { span: 24 }, sm: { span: 18 } }}>
          <Form.Item
            name="name"
            label="唯一标识"
            rules={[
              {
                required: true,
                pattern: /^[a-z]([a-z0-9_-]){0,62}[a-z0-9]$/,
                message: '由小写字母、数字、中横线、下划线组成，字母开头、字母或数据结尾，长度范围为2~64',
              },
            ]}
          >
            <Input disabled={editType === NodeMenu.EDIT} />
          </Form.Item>
          <Form.Item
            name="alias"
            label="显示名称"
            rules={[
              {
                max: 64,
                message: '最多64个字符',
              },
            ]}
          >
            <Input />
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
            <Input.TextArea rows={3} maxLength={6} />
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
            label="绝对叶子结点"
            valuePropName="checked"
            help="勾选后该结点不允许新增叶子结点，且唯一标识也是全局唯一"
          >
            <Checkbox disabled={editType === NodeMenu.EDIT} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

TreeView.propTypes = {
  onSelect: PropTypes.func,
};

export default TreeView;
