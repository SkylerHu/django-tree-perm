import React from 'react';
import { Row, Col } from 'antd';
import TreeView from './TreeView';


function App() {
  return (
    <Row>
      <Col span={8}>
        <TreeView />
      </Col>
    </Row>
  );
}

export default App;
