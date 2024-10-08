import React, { useState, useMemo, forwardRef, useImperativeHandle, useCallback, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Spin, Descriptions, List, Card, Row, Col, Button, Modal, Form, Input, Checkbox } from 'antd';

import { useProtect } from './restful-antd/hooks';
import requests from './restful-antd/requests';
import { TreeApi, COMMON_FORM_COL_PROPS } from './tools';

const NodeView = forwardRef(({ path }, ref) => {
  const [protect] = useProtect();
  const [loading, setLoading] = useState(false);
  const [node, setNode] = useState({});

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

  useImperativeHandle(
    ref,
    () => ({
      fetchNodeDetail: fetchNodeDetail,
    }),
    [fetchNodeDetail],
  );

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
        children: node.name,
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
        children: node.path,
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
    <Spin tip="加载中" spinning={loading}>
      <div className="cls-view-match-parent">
        <Descriptions title={<div className="cls-common-title">基本信息</div>} bordered column={3} items={descItems} />
        <List
          header={(
            <Row>
              <Col flex="auto"><div className="cls-common-title">角色成员</div></Col>
              <Col flex="100px">
                <Button
                  type="primary"
                  onClick={() => setRoleModalVisiable(true)}
                >新增角色</Button>
              </Col>
            </Row>
          )}
          grid={2}
          dataSource={[]}
          renderItem={item => (
            <List.Item>
              <Card title={item.title}>Card content</Card>
            </List.Item>
          )}
        />
        <Modal
          title="管理角色"
          width="50%"
          maskClosable={false}
          destroyOnClose
          confirmLoading={loading}
          open={roleModalVisiable}
          onOk={() => {
            onRoleModalClose();
          }}
          onCancel={() => onRoleModalClose()}
        >
          <Form form={roleFormRef} {...COMMON_FORM_COL_PROPS}>
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
              <Input />
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
          </Form>
        </Modal>
      </div>
    </Spin>
  );
});

NodeView.displayName = 'NodeView';
NodeView.propTypes = {
  path: PropTypes.string,
  onChange: PropTypes.func,
};

export default NodeView;
