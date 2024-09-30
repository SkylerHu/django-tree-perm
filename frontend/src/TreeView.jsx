import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { PlusOutlined } from '@ant-design/icons';
import { message, Tree, Input, Row, Col, Button, Modal, Form, Checkbox } from 'antd';

import SelectView from './restful-antd/components/SelectView'
import { useProtect } from './restful-antd/hooks'
import requests, { formatRequestError } from './restful-antd/requests'


const TreeView = ({
  onSelect = () => {},
}) => {

  const [protect] = useProtect();
  const [loading, setLoading] = useState(false);
  const [editModalVisiable, setEditModalVisiable] = useState(false);
  const [formRef] = Form.useForm();


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
      <Tree
        treeData={[]}
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
            requests.post('tree/nodes/', values).then(protect((resp) => {
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
            <SelectView restful='tree/nodes/'/>
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
