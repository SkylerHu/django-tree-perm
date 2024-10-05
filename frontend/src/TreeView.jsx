import React, { useCallback, useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { PlusOutlined, SettingOutlined } from '@ant-design/icons';
import { message, Tree, Input, Row, Col, Button, Modal, Form, Checkbox, Space, Dropdown } from 'antd';

import * as Enum from 'js-enumerate';

import SelectView from './restful-antd/components/SelectView'
import { useProtect } from './restful-antd/hooks'
import requests, { formatRequestError } from './restful-antd/requests'
import { TreeApi } from './constants';

const NodeMenu = new Enum([
  { key: 'EDIT', value: 'edit', label: '修改信息' },
  { key: 'ADD', value: 'add', label: '添加结点' },
  { key: 'DELETE', value: 'delete', label: '删除结点', danger: true },
]);

/**
 * 向树结构数据treeData中，将nodes插入作为某结点的chi˜ldren
 * @param {*} treeData
 * @param {*} parent_path
 * @param {*} nodes
 * @returns
 */
const insertChildren = (treeData, parent_path, nodes) => {
  // 递归查找结点
  const findNode = (data, path) => {
    for (let i = 0; i < data.length; i++) {
      const node = data[i];
      if (node.path === path) {
        return node;
      }
      if (node.path && node.path.startsWith(path) && node.children) {
        return findNode(node.children, path)
      }
    }
    return null;
  };

 const ret = findNode(treeData, parent_path);
 if (!ret) {
  return nodes;
 }
 ret.children = nodes;
 return treeData;
};


const TreeView = ({
  onSelect = () => {},
}) => {

  const [protect] = useProtect();
  const [loading, setLoading] = useState(false);
  // 编辑表单
  const [editModalVisiable, setEditModalVisiable] = useState(false);
  const [formRef] = Form.useForm();
  // 编辑的结点
  const [editNode, setEditNode] = useState();
  // 树结构数据
  const [treeData, setTreeData] = useState([]);

  useEffect(() => {
    requests.get(TreeApi.LAZY_LOAD).then(resp => {
      const nodes = resp.data.results;
      setTreeData(nodes);
    });
  }, [])

  return (
    <div style={{ width: '100%', height: '100%', padding: 10 }}>
      <Row gutter={10}>
        <Col span={20}>
          <Input.Search
            styles={{ width: '100%' }}
            placeholder="输入关键字进行搜索"
            onSearch={(value) => {

            }}
            enterButton
          />
        </Col>
        <Col span={4}>
          <Button
            type="primary" icon={<PlusOutlined />}
            onClick={() => setEditModalVisiable(true)}
          />
        </Col>
      </Row>
      <div style={{ height: 10 }}/>
      <Tree
        treeData={treeData}
        fieldNames={{
          title: 'name',
          key: 'id',
        }}
        titleRender={(node) => (
          <Space>
            <div>{node.alias ? `${node.name} (${node.alias})` : node.name}</div>
            <Dropdown
              menu={{
                items: NodeMenu.options,
                onClick: (menu) => {
                  switch(menu.key) {
                    case 'edit': {
                      break;
                    }
                    case 'add_child': {
                      break;
                    }
                    case 'delete': {
                      break;
                    }
                    default:
                      break;
                  }
                },
              }}
            >
              <SettingOutlined />
            </Dropdown>
          </Space>
        )}
        loadData={(node) => new Promise((resolve) => {
          if (node.children) {
            resolve();
            return;
          }
          requests.get(TreeApi.LAZY_LOAD, { params: { parent_path: node.path } }).then(protect(resp => {
            const nodes = resp.data.results;
            setTreeData((oldData) => {
              insertChildren(oldData, node.path, nodes)
              return oldData;
            });
          })).finally(protect(() => resolve()));
        })}
      />
      <Modal
        title="新增结点"
        destroyOnClose
        width="50%"
        confirmLoading={loading}
        open={editModalVisiable}
        onOk={() => {
          formRef.validateFields().then(protect((values) => {
            setLoading(true);
            requests.post(TreeApi.NODE_LIST, values).then(protect((resp) => {
              message.success("操作成功");
              setEditModalVisiable(false);
            }), protect((error) => {
              const { err_msg } = formatRequestError(error);
              message.error(`操作失败，请重试. ${err_msg}`)
            })).finally(protect(() => setLoading(false)));
          }), protect(() => {
            message.error('请正确填写表单');
          }));
        }}
        onCancel={() => setEditModalVisiable(false)}

      >
        <Form
          form={formRef}
          labelCol={{ flex: '120px' }}
          wrapperCol={{ xs: { span: 24 }, sm: { span: 18 } }}
        >
          <Form.Item
            name="name" label="唯一标识"
            rules={[
              {
                required: true,
                pattern: /^[a-z]([a-z0-9_-]){0,62}[a-z0-9]$/,
                message: '由小写字母、数字、中横线、下划线组成，字母开头、字母或数据结尾，长度范围为2~64'
              }
            ]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="alias" label="显示名称"
            rules={[
              {
                max: 64,
                message: '最多64个字符'
              }
            ]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="description" label="描述"
            rules={[
              {
                max: 1024,
                message: '最多1024个字符'
              }
            ]}
          >
            <Input.TextArea rows={3} maxLength={6}/>
          </Form.Item>
          <Form.Item
            name="parent_id" label="父结点"
            help="无父类结点则新增的是根结点"
          >
            <SelectView restful={TreeApi.NODE_LIST} fieldNames={{ label: 'path', value: 'name' }}/>
          </Form.Item>
          <Form.Item
            name="is_key" label="绝对叶子结点"
            valuePropName="checked"
            help="勾选后该结点不允许新增叶子结点，且唯一标识也是全局唯一"
          >
            <Checkbox />
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
