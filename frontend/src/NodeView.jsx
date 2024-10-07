import React, { useState, useMemo, forwardRef, useImperativeHandle, useCallback, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Spin, Descriptions } from 'antd';

// import * as Enum from 'js-enumerate';

import { useProtect } from './restful-antd/hooks';
import requests from './restful-antd/requests';
import { TreeApi } from './tools';

const NodeView = forwardRef(({ path }, ref) => {
  const [protect] = useProtect();
  const [loading, setLoading] = useState(false);
  const [node, setNode] = useState({});

  const fetchNodeDetail = useCallback((value) => {
    if (!value) {
      setNode({});
      return;
    }
    setLoading(true);
    requests.get(TreeApi.nodeDetail(value)).then(protect(resp => {
      setNode(resp.data);
      setLoading(false);
    }));
  }, [protect]);

  useImperativeHandle(ref, () => ({
    fetchNodeDetail: fetchNodeDetail,
  }), [fetchNodeDetail]);

  useEffect(() => {
    fetchNodeDetail(path);
  }, [path, fetchNodeDetail]);

  const descItems = useMemo(() => {
    const items = [
      {
        key: 'name',
        label: '标识',
        children: node?.name,
      },
      {
        key: 'alias',
        label: '别名',
        children: node?.alias,
      },
      {
        key: 'at',
        label: '时间',
        children: (
          <div>
            <div>创建：{node?.created_at}</div>
            <div>更新：{node?.updated_at}</div>
          </div>
        ),
      },
      {
        key: 'is_key',
        label: '是否Key',
        children: node?.is_key ? '是' : '否',
      },
      {
        key: 'path',
        label: '路径',
        span: 2,
        children: node?.path,
      },
      {
        key: 'description',
        label: '描述',
        span: 3,
        children: node?.description,
      },
    ];
    return items;
  }, [node]);

  if (!node?.id) {
    return <div>请点击选择结点</div>;
  }

  return (
    <Spin tip="加载中" spinning={loading}>
      <div className="cls-view-match-parent">
        <Descriptions title="基本信息" bordered column={3} items={descItems} />
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
