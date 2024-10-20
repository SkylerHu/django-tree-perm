
import { notification } from 'antd';
import axios from 'axios';

export function formatRequestError (error) {
  let errMsg = error.message;
  if (error.response) {
    const status = error.response.status;
    let msg = '';
    switch (status) {
      case 401: {
        msg = '未登录';
        break;
      }
      case 403: {
        msg = '未授权/禁止操作';
        break;
      }
      case 404: {
        msg = `${error.config.url}`;
        break;
      }
      default: {
        msg = error.response.data;
        if (msg instanceof Object ) {
          msg = JSON.stringify(msg);
        }
        break;
      }
    }
    if (error.response.status) {
      errMsg = `HttpError(${status}): ${msg}`;
    }

  }
  return { errMsg };
}


const instance = axios.create({
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
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
    let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!csrftoken) {
      csrftoken = getCookie('csrftoken');
    }
    headers['X-CSRFToken'] = csrftoken;
  }

  config.headers = headers;

  return config;
});
instance.interceptors.response.use((response) => {
  return response;
}, (error) => {
  const { errMsg } = formatRequestError(error);
  const config = {
    message: '操作失败，请重试',
    description: errMsg,
  };
  if (error?.response?.status === 401) {
    config.key = '401';
  } else if (error?.response?.status === 403) {
    config.key = '403';
  }
  notification.error(config);
  return Promise.reject(error);
});



export default instance;
