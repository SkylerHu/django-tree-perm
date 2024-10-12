import React, { useState, useMemo, forwardRef, useImperativeHandle, useCallback, useEffect } from 'react';
import PropTypes from 'prop-types';
import { CopyOutlined } from '@ant-design/icons';
import { Spin, Descriptions, List, Row, Col, Button, Modal, Form, message } from 'antd';

import { useProtect } from './restful-antd/hooks';
import requests from './restful-antd/requests';
import { TreeApi, COMMON_FORM_COL_PROPS, COMMON_MODAL_PROPS } from './tools';
import RoleUser, { RoleEditView } from './RoleUser';

const LIST_PAGE_SIZE = 100;

async function copyTextToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    message.success(`成功拷贝: ${text}`);
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('Failed to copy text: ', err);
  }
}

const NodeView = forwardRef(({ path }, ref) => {
  const [protect] = useProtect();
  const [loading, setLoading] = useState(false);
  const [node, setNode] = useState({});

  const [roleLoading, setRoleLoading] = useState(false);
  const [rolesData, setRolesData] = useState({});
  const [roleFormRef] = Form.useForm();
  const [roleModalVisiable, setRoleModalVisiable] = useState(false);

  const fetchNodeDetail = useCallback(
    value => {
      if (!value) {
        setNode({});
        return;
      }
      setLoading(true);
      requests.get(TreeApi.nodeDetail(value)).then(
        protect(resp => {
          setNode(resp.data);
          setLoading(false);
        }),
      );
    },
    [protect],
  );

  const fetchRoles = useCallback(() => {
    setRoleLoading(true);
    requests.get(TreeApi.ROLES).then(
      protect(resp => {
        setRolesData(resp.data);
        setRoleLoading(false);
      }),
    );
  }, [protect]);

  useImperativeHandle(
    ref,
    () => ({
      fetchNodeDetail: fetchNodeDetail,
    }),
    [fetchNodeDetail],
  );

  useEffect(() => {
    fetchRoles();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    fetchNodeDetail(path);
  }, [path, fetchNodeDetail]);

  const onRoleModalClose = useCallback(() => {
    setRoleModalVisiable(false);
    roleFormRef.resetFields();
  }, [roleFormRef]);

  const descItems = useMemo(() => {
    const items = [
      {
        key: 'name',
        label: '标识',
        children: (
          <span>
            {node.name}
            <CopyOutlined style={{ marginLeft: 5 }} onClick={() => copyTextToClipboard(node.name)}/>
          </span>
        ),
      },
      {
        key: 'alias',
        label: '别名',
        children: node.alias,
      },
      {
        key: 'at',
        label: '时间',
        children: (
          <div>
            <div>创建：{node.created_at}</div>
            <div>更新：{node.updated_at}</div>
          </div>
        ),
      },
      {
        key: 'is_key',
        label: '是否Key',
        children: node.is_key ? '是' : '否',
      },
      {
        key: 'path',
        label: '路径',
        span: 2,
        children: (
          <span>
            {node.path}
            <CopyOutlined style={{ marginLeft: 5 }} onClick={() => copyTextToClipboard(node.path)}/>
          </span>
        ),
      },
      {
        key: 'description',
        label: '描述',
        span: 3,
        children: node.description,
      },
    ];
    return items;
  }, [node]);

  if (!node.id) {
    return <div>请点击选择结点</div>;
  }

  return (
    <div className="cls-scoll-container">
      <div className="cls-scoll-container-wrapper">
        <div className="cls-scoll-container-content">
          <Spin spinning={loading}>
            <Descriptions
              title={<div className="cls-common-title">基本信息</div>}
              bordered
              column={3}
              items={descItems}
            />
          </Spin>
          <Spin spinning={roleLoading}>
            <List
              className="cls-role-list-view"
              header={
                <Row>
                  <Col flex="auto">
                    <div className="cls-common-title">角色成员</div>
                  </Col>
                  <Col flex="100px">
                    <Button type="primary" onClick={() => setRoleModalVisiable(true)}>
                      新增角色
                    </Button>
                  </Col>
                </Row>
              }
              grid={{ gutter: 10, column: 3 }}
              dataSource={rolesData.results}
              loading={roleLoading}
              renderItem={item => (
                <List.Item>
                  <RoleUser role={item} node={node} onRoleDelete={(data) => {
                    setRolesData(oldData => ({
                      ...oldData,
                      results: oldData.results.filter(row => row.id !== data.id),
                    }));
                  }}/>
                </List.Item>
              )}
              pagination={rolesData.count > LIST_PAGE_SIZE ? { pageSize: LIST_PAGE_SIZE } : false}
            />
          </Spin>
        </div>
      </div>
      <Modal
        title="新增角色"
        {...COMMON_MODAL_PROPS}
        confirmLoading={roleLoading}
        open={roleModalVisiable}
        onOk={() => {
          roleFormRef.validateFields().then(
            protect(values => {
              setRoleLoading(true);
              requests
                .post(TreeApi.ROLES, values)
                .then(
                  protect(() => {
                    message.success('新增角色成功');
                    onRoleModalClose();
                    fetchRoles();
                  }),
                )
                .finally(protect(() => setRoleLoading(false)));
            }),
          );
        }}
        onCancel={() => onRoleModalClose()}
      >
        <Form form={roleFormRef} {...COMMON_FORM_COL_PROPS}>
          <RoleEditView />
        </Form>
      </Modal>
    </div>
  );
});

NodeView.displayName = 'NodeView';
NodeView.propTypes = {
  path: PropTypes.string,
  onChange: PropTypes.func,
};

export default NodeView;
