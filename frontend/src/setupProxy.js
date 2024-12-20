// // 你无需在任何位置导入此文件。 它在启动开发服务器时会自动注册
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  if (process.env.NODE_ENV !== 'production') {
    app.use(
      '/tree',
      createProxyMiddleware({
        target: 'http://127.0.0.1:8000/tree/tree',
        changeOrigin: true,
        logLevel: 'debug',
      })
    );
  }
};
