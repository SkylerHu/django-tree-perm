import React, { useState, useCallback, useEffect } from 'react';
import PropTypes from 'prop-types';
import { UsergroupAddOutlined, UsergroupDeleteOutlined, EditOutlined, DeleteOutlined, UserOutlined } from '@ant-design/icons';
import { Form, Input, Checkbox, Modal, Spin, Card, Tag, Tooltip, Button, Row, Col, Space, message, Flex, Popconfirm } from 'antd';

import * as Enum from 'js-enumerate';

import SelectView from './restful-antd/components/SelectView';
import { useProtect } from './restful-antd/hooks';
import requests from './restful-antd/requests';
import { TreeApi, COMMON_FORM_COL_PROPS, COMMON_MODAL_PROPS } from './tools';

const RoleEditType = new Enum([
  { key: 'ROLE', value: 'role', label: '编解角色' },
  { key: 'ADD_USER', value: 'add_user', label: '新增关联用户' },
  { key: 'DEL_USER', value: 'del_user', label: '删除关联用户' },
]);

// 角色表单 用于新增和编辑
const RoleEditView = ({ isEdit = false }) => {
  return (
    <>
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
        <Input disabled={isEdit} count={{ show: true, max: 64 }}/>
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
        <Input.TextArea autoSize={{ minRows: 3, maxRows: 6 }} count={{ show: true, max: 1024 }} />
      </Form.Item>
      <Form.Item
        name="can_manage"
        label="允许管理结点"
        valuePropName="checked"
      >
        <Checkbox>勾选后，该角色下的所有成员可对结点进行管理，包括删除操作</Checkbox>
      </Form.Item>
    </>
  );
};

RoleEditView.propTypes = {
  isEdit: PropTypes.bool,
};

// 用于角色展示信息
const getRoleLabel = role => {
  let label = role.alias ? `${role.name} (${role.alias})` : role.name;
  return label;
};

// 用户展示信息
const getUserLabel = user => {
  let label = user.username;
  if (user.first_name || user.last_name) {
    label = `${label}(${user.first_name}${user.last_name})`;
  }
  return label;
};


const RoleUser = ({ user, role, node, onRoleDelete }) => {
  const [protect] = useProtect();
  const [loading, setLoading] = useState(false);
  // 角色数据
  const [data, setData] = useState({ ...role });
  // 打开编辑弹窗
  const [openModal, setOpenModal] = useState();
  const [roleFormRef] = Form.useForm();
  // 在结点下的角色关联新的用户
  const [addUsersRef] = Form.useForm();

  const fetchRoleDetail = useCallback((force = false) => {
    if (!role.id || !node.id) {
      setData({});
      return;
    }
    if (!force && role.user_set !== undefined) {
      // 刚开始是准备在各个Role独占获取用户列表；后来因发现删除role或导致后面的role都会刷新，所以放到了最外层获取数据
      return;
    }
    setLoading(true);
    requests.get(TreeApi.roleDetail(role.id, node.id), { params: { path: node.path, name: role.name } }).then(
      protect(resp => {
        setData(resp.data);
        setLoading(false);
      }),
    );
  }, [protect, role, node]);

  useEffect(() => {
    fetchRoleDetail();
  }, [fetchRoleDetail]);

  useEffect(() => {
    setData(role);
  }, [role]);

  return (
    <Spin spinning={loading}>
      <Card
        title={
          <Row wrap={false}>
            <Col flex="auto">
              <span>
                <Tooltip title={data.description}>{getRoleLabel(data)}</Tooltip>
                {
                  data.can_manage && (
                    <Tooltip title="该角色用户可以管理结点">
                      <UserOutlined style={{ color: 'green', marginLeft: 5 }} />
                    </Tooltip>
                  )
                }
              </span>
            </Col>
            <Col flex={ user.tree_manager ? '120px' : (user.node_manager ? '60px' : '0px')}>
              <Space size="small">
                {
                  (user.tree_manager || user.node_manager) && (
                    <>
                      <Button
                        size="small"
                        icon={<UsergroupAddOutlined />}
                        onClick={() => setOpenModal(RoleEditType.ADD_USER)}
                      />
                      <Tooltip title="点击后可操作删除关联用户">
                        <Button
                          size="small"
                          icon={<UsergroupDeleteOutlined />}
                          style={openModal === RoleEditType.DEL_USER ? { color: 'red' } : null}
                          onClick={() => (openModal ? setOpenModal(null) : setOpenModal(RoleEditType.DEL_USER))}
                        />
                      </Tooltip>
                    </>
                  )
                }
                {
                  user.tree_manager && (
                    <>
                      <Button
                        size="small"
                        icon={<EditOutlined />}
                        onClick={() => {
                          setOpenModal(RoleEditType.ROLE);
                          roleFormRef.setFieldsValue(data);
                        }}
                      />
                      <Popconfirm
                        title="确认删除"
                        description={`操作删除角色 ${data.name} ?`}
                        okText="确认"
                        cancelText="取消"
                        onConfirm={() => {
                          requests.delete(TreeApi.roleDetail(data.id), { params: { name: data.name } }).then(protect(() => {
                            if (onRoleDelete) {
                              onRoleDelete(role);
                            }
                          }));
                        }}
                      >
                        <Button
                          size="small"
                          icon={<DeleteOutlined />}
                          style={{ color: 'red' }}
                          onClick={() => (openModal ? setOpenModal(null) : setOpenModal(RoleEditType.DEL_USER))}
                        />
                      </Popconfirm>
                    </>
                  )
                }
              </Space>
            </Col>
          </Row>
        }
      >
        <Flex wrap gap={5} className="cls-view-match-parent">
          {data.user_set?.map(item => (
            <Tag
              key={item.id}
              color={item.node_id === node.id ? 'blue' : null}
              closeIcon={openModal === RoleEditType.DEL_USER && item.node_id === node.id}
              onClose={e => {
                e.preventDefault();
                requests
                  .delete(TreeApi.delUserRole(item.id), {
                    params: { username: item.user?.username, path: node.path, name: data.name },
                  })
                  .then(
                    protect(() => {
                      setData(oldData => ({
                        ...oldData,
                        // eslint-disable-next-line camelcase
                        user_set: oldData.user_set.filter(row => row.id !== item.id),
                      }));
                    }),
                  );
              }}
            >
              {item.node_id === node.id ? (
                getUserLabel(item.user)
              ) : (
                <Tooltip title={`继承自: ${item.node.path}`} color="#fff" overlayInnerStyle={{ color: '#000', whiteSpace: 'nowrap' }}>
                  {getUserLabel(item.user)}
                </Tooltip>
              )}
            </Tag>
          ))}
        </Flex>
      </Card>
      <Modal
        title="编辑角色"
        {...COMMON_MODAL_PROPS}
        confirmLoading={loading}
        open={openModal === RoleEditType.ROLE}
        onOk={() => {
          roleFormRef.validateFields().then(
            protect(values => {
              setLoading(true);
              requests
                .patch(TreeApi.roleDetail(data.id), values, { params: { name: data.name, path: node.path } })
                .then(
                  protect(resp => {
                    message.success('修改成功');
                    setOpenModal(null);
                    // eslint-disable-next-line camelcase
                    setData(oldData => ({ user_set: oldData.user_set, ...resp.data }));
                  }),
                )
                .finally(protect(() => setLoading(false)));
            }),
          );
        }}
        onCancel={() => setOpenModal(null)}
      >
        <Form form={roleFormRef} {...COMMON_FORM_COL_PROPS}>
          <RoleEditView isEdit />
        </Form>
      </Modal>
      <Modal
        title="新增关联用户"
        {...COMMON_MODAL_PROPS}
        confirmLoading={loading}
        open={openModal === RoleEditType.ADD_USER}
        onOk={() => {
          addUsersRef.validateFields().then(
            protect(values => {
              setLoading(true);
              requests
                .post(TreeApi.ROLE_USER, {
                  ...values,
                  node_id: node.id, // eslint-disable-line camelcase
                  role_id: data.id, // eslint-disable-line camelcase
                // eslint-disable-next-line camelcase
                }, { params: { path: node.path, role_name: data.name } })
                .then(
                  protect(() => {
                    message.success('关联成功');
                    setOpenModal(null);
                    fetchRoleDetail(true);
                  }),
                )
                .finally(protect(() => setLoading(false)));
            }),
          );
        }}
        onCancel={() => setOpenModal(null)}
      >
        <Form form={addUsersRef} {...COMMON_FORM_COL_PROPS}>
          <Form.Item name="user_ids" label="用户" rules={[{ required: true }]}>
            <SelectView
              mode="multiple"
              restful={TreeApi.USERS}
              fieldNames={{ value: 'id', label: 'username' }}
              antdSelectProps={{
                style: { width: '100%' },
                optionRender: option => getUserLabel(option.data),
              }}
            />
          </Form.Item>
        </Form>
      </Modal>
    </Spin>
  );
};

RoleUser.propTypes = {
  // 用于控制权限
  user: PropTypes.object,
  role: PropTypes.object.isRequired,
  node: PropTypes.object.isRequired,
  // 删除操作的事件
  onRoleDelete: PropTypes.func,
};

export { RoleEditView };
export default RoleUser;
