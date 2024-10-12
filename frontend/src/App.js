import React, { useState, useRef } from 'react';
import { Row, Col } from 'antd';

import queryString from 'query-string';

import TreeView from './TreeView';
import NodeView from './NodeView';

function App() {

  const [path, setPath] = useState(queryString.parse(window.location.search)?.path);

  const nodeRef = useRef();

  return (
    <Row style={{ height: '100%', padding: 10 }} gutter={20}>
      <Col span={6}>
        <TreeView
          defaultValue={path}
          onChange={({ path: value }) => {
            if (path === value) {
              nodeRef.current?.fetchNodeDetail(value);
            } else {
              setPath(value);
            }
            const location = window.location;
            let targetHref = `${location.pathname}${location.hash}`;
            if (value) {
              targetHref = `${targetHref}?path=${value}`;
            }
            // 需要保证不能刷新页面
            history.pushState(null, null, targetHref);
            // window.location.href = `${location.pathname}${location.hash}?path=${path}`;
          }}
        />
      </Col>
      <Col span={18}>
        <NodeView ref={nodeRef} path={path}/>
      </Col>
    </Row>
  );
}

export default App;
