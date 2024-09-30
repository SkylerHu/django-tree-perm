import axios from 'axios';

export function formatRequestError (error) {
  let err_msg = error.message;
  if (error.response) {
    const status = error.response.status;
    let msg = '';
    switch (status) {
      case 401: {
        msg = '未登录';
        break
      }
      case 403: {
        msg = '未授权禁止操作';
        break
      }
      default: {
        msg = error.response.data;
        if (msg instanceof Object ) {
          msg = JSON.stringify(msg);
        }
        break;
      }
    }
    if (error.response.status)
    err_msg = `HttpError(${status}): ${msg}`;
  }
  return { err_msg };
}


const instance = axios.create({
  timeout: 10000,
  headers: {'Content-Type': 'application/json'},
});


function getCookie (name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

instance.interceptors.request.use((config) => {

  const headers = { ...config.headers };

  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(config.method.toUpperCase())) {
    const csrftoken = getCookie('csrftoken');
    headers['X-CSRFToken'] = csrftoken;
  }

  config.headers = headers;

  return config;
});



export default instance;
