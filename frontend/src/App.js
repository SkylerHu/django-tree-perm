import React from 'react';
import { Row, Col } from 'antd';
import TreeView from './TreeView';


function App() {
  return (
    <Row style={{ width: '100%', height: '100%' }}>
      <Col span={6}>
        <TreeView />
      </Col>
    </Row>
  );
}

export default App;
