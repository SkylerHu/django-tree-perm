import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Row, Col, Form, Input, Modal, message } from 'antd';

import queryString from 'query-string';

import { useProtect } from './restful-antd/hooks';
import requests from './restful-antd/requests';
import { TreeApi, COMMON_FORM_COL_PROPS, TREE_SPLIT_NODE_FLAG } from './tools';
import TreeView from './TreeView';
import NodeView from './NodeView';

function App() {

  // 记录浏览器地址栏的参数
  const [path, setPath] = useState(queryString.parse(window.location.search)?.path);

  const nodeRef = useRef();

  const [protect] = useProtect();
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState({});
  const [showLogin, setShowLogin] = useState(false);
  const [loginFormRef] = Form.useForm();

  const fetchUserInfo = useCallback(() => {
    setLoading(true);
    requests.get(TreeApi.USER_PERM, { params: { path } }).then(protect(resp => {
      setUser(resp.data.user);
    }), protect((err) => {
      if (err?.response?.status === 401) {
        setShowLogin(true);
      }
    })).finally(protect(() => setLoading(false)));
  }, [path, protect]);

  useEffect(() => {
    fetchUserInfo();
  }, [fetchUserInfo, path]);

  return (
    <div className="cls-view-match-parent">
      <Row style={{ height: '100%', padding: 10 }} gutter={20}>
        <Col span={6}>
          <TreeView
            user={user}
            defaultValue={path}
            onChange={({ path: value }) => {
              if (path === value) {
                nodeRef.current?.fetchNodeDetail(value);
              } else {
                setPath(value);
              }
              const location = window.location;
              let targetHref = `${location.pathname}${location.hash}`;
              if (value && value.indexOf(TREE_SPLIT_NODE_FLAG) > -1) {
                targetHref = `${targetHref}?path=${value}`;
              }
              // 需要保证不能刷新页面
              history.pushState(null, null, targetHref);
              // window.location.href = `${location.pathname}${location.hash}?path=${path}`;
            }}
          />
        </Col>
        <Col span={18}>
          <NodeView ref={nodeRef} user={user} path={path}/>
        </Col>
      </Row>
      <Modal
        title="新增角色"
        confirmLoading={loading}
        open={showLogin}
        onOk={() => {
          loginFormRef.validateFields().then(
            protect(values => {
              setLoading(true);
              requests
                .post(TreeApi.USER_PERM, values)
                .then(
                  protect(() => {
                    message.success('登录成功');
                    setShowLogin(false);
                    // 刷新页面
                    location.reload();
                  }),
                )
                .finally(protect(() => setLoading(false)));
            }),
          );
        }}
        onCancel={() => setShowLogin(false)}
      >
        <Form form={loginFormRef} {...COMMON_FORM_COL_PROPS}>
          <Form.Item
            name="username"
            label="用户名"
            rules={[{ required: true }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="password"
            label="密码"
            rules={[{ required: true }]}
          >
            <Input.Password />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default App;
