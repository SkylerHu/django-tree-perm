// 树层级分隔符
export const TREE_SPLIT_NODE_FLAG = '.';

// 定义接口
export const TreeApi = {
  USER_PERM: 'tree/perm/',
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

// form通用样式
export const COMMON_FORM_COL_PROPS = {
  labelCol: { flex: '120px' },
  wrapperCol: { xs: { span: 24 }, sm: { span: 18 } },
};

// modal通用样式
export const COMMON_MODAL_PROPS = {
  width: '50%',
  destroyOnClose: true,
  maskClosable: true,
};

/**
 * 根据path获取父类path
 */
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
