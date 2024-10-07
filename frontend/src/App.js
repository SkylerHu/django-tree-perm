import React, { useState } from 'react';
import { Row, Col } from 'antd';

import queryString from 'query-string';

import TreeView from './TreeView';
import NodeView from './NodeView';

function App() {
  const [path, setPath] = useState(queryString.parse(window.location.search)?.path);

  return (
    <Row style={{ height: '100%', padding: 10 }} gutter={20}>
      <Col span={6}>
        <TreeView
          defaultValue={path}
          onChange={({ path: value }) => {
            setPath(value);
            if (value) {
              const location = window.location;
              const targetHref = `${location.pathname}${location.hash}?path=${value}`;
              // 需要保证不能刷新页面
              history.pushState(null, null, targetHref);
              // window.location.href = `${location.pathname}${location.hash}?path=${path}`;
            }
          }}
        />
      </Col>
      <Col span={18}>
        <NodeView path={path}/>
      </Col>
    </Row>
  );
}

export default App;
