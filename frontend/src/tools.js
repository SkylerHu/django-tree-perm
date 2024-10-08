export const TREE_SPLIT_NODE_FLAG = '.';

export const TreeApi = {
  NODE_LIST: 'tree/nodes/',
  nodeDetail: (pathOrId) => `tree/nodes/${pathOrId}/`,
  LAZY_LOAD: 'tree/lazyload/',
  LOAD_ALL: 'tree/load/',
};

export const COMMON_FORM_COL_PROPS = {
  labelCol: { flex: '120px' },
  wrapperCol: { xs: { span: 24 }, sm: { span: 18 } },
};

export const getPathParent = (path) => {
  if (!path) {
    return '';
  }
  const arr = path.split(TREE_SPLIT_NODE_FLAG);
  if (arr.length <= 1) {
    return '';
  }
  // 去掉最后一个
  arr.pop();
  return arr.join(TREE_SPLIT_NODE_FLAG);
};
