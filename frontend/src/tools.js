export const TREE_SPLIT_NODE_FLAG = '.';

export const TreeApi = {
  NODE_LIST: 'tree/nodes/',
  nodeDetail: (pathOrId) => `tree/nodes/${pathOrId}/`,
  LAZY_LOAD: 'tree/lazyload/',
  LOAD_ALL: 'tree/load/',
  ROLES: 'tree/roles/',
  roleDetail: (roleId, nodeId = '') => nodeId ? `tree/roles/${roleId}/?node_id=${nodeId}` : `tree/roles/${roleId}/`,
  ROLE_USER: 'tree/noderoles/',
  delUserRole: (pk) => `tree/noderoles/${pk}/`,
  USERS: 'tree/users/',
};

export const COMMON_FORM_COL_PROPS = {
  labelCol: { flex: '120px' },
  wrapperCol: { xs: { span: 24 }, sm: { span: 18 } },
};

export const COMMON_MODAL_PROPS = {
  okText: '确认',
  cancelText: '取消',
  width: '50%',
  destroyOnClose: true,
  maskClosable: true,
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

export const getTreePaths = (path) => {
  const paths = path.split(TREE_SPLIT_NODE_FLAG);
  const arr = [];
  for (let i = 1; i <= paths.length; i++) {
    const p = paths.slice(0, i).join(TREE_SPLIT_NODE_FLAG);
    arr.push(p);
  }
  return arr;
};
