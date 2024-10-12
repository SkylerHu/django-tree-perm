import React, { useState, useCallback, useEffect } from 'react';
import PropTypes from 'prop-types';
import { UsergroupAddOutlined, UserDeleteOutlined, EditOutlined } from '@ant-design/icons';
import { Form, Input, Checkbox, Modal, Spin, Card, Tag, Tooltip, Button, Row, Col, Space, message, Flex } from 'antd';

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
        <Input disabled={isEdit} />
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
        <Input.TextArea autoSize={{ minRows: 3, maxRows: 6 }} />
      </Form.Item>
      <Form.Item
        name="can_manage"
        label="允许管理结点"
        valuePropName="checked"
        help="勾选后，该角色下的所有成员可对相应结点进行管理，包括删除操作"
      >
        <Checkbox />
      </Form.Item>
    </>
  );
};

RoleEditView.propTypes = {
  isEdit: PropTypes.bool,
};

const getRoleLabel = role => {
  let label = role.alias ? `${role.name} (${role.alias})` : role.name;
  return label;
};

const getUserLabel = user => {
  let label = user.username;
  if (user.first_name || user.last_name) {
    label = `${label}(${user.first_name}${user.last_name})`;
  }
  return label;
};

const RoleUser = ({ role, node }) => {
  const [protect] = useProtect();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState({ ...role });
  const [openModal, setOpenModal] = useState();

  const [roleFormRef] = Form.useForm();
  const [addUsersRef] = Form.useForm();

  const fetchRoleDetail = useCallback(
    () => {
      setLoading(true);
      if (!role.id || !node.id) {
        setData({});
        return;
      }
      requests.get(TreeApi.roleDetail(role.id, node.id)).then(
        protect(resp => {
          setData(resp.data);
          setLoading(false);
        }),
      );
    },
    [protect, role.id, node.id],
  );

  useEffect(() => {
    fetchRoleDetail();
  }, [fetchRoleDetail]);

  return (
    <Spin spinning={loading}>
      <Card
        title={
          <Row wrap={false}>
            <Col flex="auto">
              <Tooltip title={data.description}>{getRoleLabel(data)}</Tooltip>
            </Col>
            <Col flex="90px">
              <Space size="small">
                <Button
                  size="small"
                  icon={<EditOutlined />}
                  onClick={() => {
                    setOpenModal(RoleEditType.ROLE);
                    roleFormRef.setFieldsValue(data);
                  }}
                />
                <Button
                  size="small"
                  icon={<UsergroupAddOutlined />}
                  onClick={() => setOpenModal(RoleEditType.ADD_USER)}
                ></Button>
                <Button
                  size="small"
                  icon={<UserDeleteOutlined />}
                  style={openModal === RoleEditType.DEL_USER ? { color: 'red' } : null}
                  onClick={() => (openModal ? setOpenModal(null) : setOpenModal(RoleEditType.DEL_USER))}
                ></Button>
              </Space>
            </Col>
          </Row>
        }
      >
        <Flex wrap gap={5}>
          {data.user_set?.map(item => (
            <Tag
              key={item.id}
              color={item.node_id === node.id ? 'blue' : null}
              closeIcon={openModal === RoleEditType.DEL_USER && item.node_id === node.id}
              onClose={(e) => {
                e.preventDefault();
                requests.delete(TreeApi.delUserRole(item.id)).then(protect(() => {
                  setData(oldData => ({
                    ...oldData,
                    // eslint-disable-next-line camelcase
                    user_set: oldData.user_set.filter(row => row.id !== item.id),
                  }));
                }));
              }}
            >
              {getUserLabel(item.user)}
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
                .patch(TreeApi.roleDetail(data.id), values)
                .then(
                  protect(resp => {
                    message.success('修改成功');
                    setOpenModal(null);
                    // eslint-disable-next-line camelcase
                    setData(oldData => ({ ...resp.data, user_set: oldData.user_set }));
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
                })
                .then(
                  protect(resp => {
                    message.success('关联成功');
                    setOpenModal(null);
                    // eslint-disable-next-line camelcase
                    setData(oldData => ({ ...resp.data, user_set: oldData.user_set }));
                    fetchRoleDetail();
                  }),
                )
                .finally(protect(() => setLoading(false)));
            }),
          );
        }}
        onCancel={() => setOpenModal(null)}
      >
        <Form form={addUsersRef} {...COMMON_FORM_COL_PROPS}>
          <Form.Item
            name="user_ids"
            label="用户"
            rules={[{ required: true }]}
          >
            <SelectView
              mode="multiple"
              restful={TreeApi.USERS}
              fieldNames={{ value: 'id', label: 'username' }}
              antdSelectProps={{
                style: { width: '100%' },
                optionRender: (option) => getUserLabel(option.data),
              }}
            />
          </Form.Item>
        </Form>
      </Modal>
    </Spin>
  );
};

RoleUser.propTypes = {
  role: PropTypes.object.isRequired,
  node: PropTypes.object.isRequired,
};

export { RoleEditView };
export default RoleUser;
