import axios from 'axios'
import { ElLoading } from 'element-plus' 

let loadingInstance = null;

const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

// 添加请求拦截器
request.interceptors.request.use(function (config) {
  // 请求发出前，开启加载动画
  loadingInstance = ElLoading.service({
      lock: true,
      text: '数据加载中...',
      background: 'rgba(6, 13, 26, 0.85)',
    });
  return config;
}, function (error) {
  return Promise.reject(error);
});

// 添加响应拦截器
request.interceptors.response.use(function (response) {
  // 响应完成后，关闭加载动画
  if (loadingInstance) loadingInstance.close();
  return response;
}, function (error) {
  if (loadingInstance) loadingInstance.close();
  return Promise.reject(error);
});

export default request