/**
  * axios 实例
  * 1. 创建 axios 实例
  * 2. 请求拦截器（可选）
  * 3. 响应拦截器（可选）
  * 4. 导出实例
  */

import axios from 'axios';
import router from '../router';

const base_url = 'http://127.0.0.1:5000';// 根据实际情况修改

// 创建 axios 实例
const Axios = axios.create({
  baseURL: base_url+'/api', // 替换为后端 API 地址
  timeout: 5000,
  withCredentials: true,
});

// 响应拦截器（可选，根据实际情况添加）
Axios.interceptors.response.use(
  (response) => {
    // 正常响应直接返回
    return response;
  },
  (error) => {
    console.error('请求出错:', error);
    console.error(error.response);
    /* 对于422缺少参数和401未授权的请求，将路由重新push到login，不抛出错误 */
    // 检查是否返回 401 Unauthorized
    if (error.response && error.response.status === 401) {
      console.warn('未授权访问，跳转到登录页面');
      // 跳转到登录页面
      router.push('/login'); 
      // return {data: {resultCode: 401, message: '未授权访问'}};
    }
    if (error.response && error.response.status === 422) {
      console.warn('缺少参数');
      // 跳转到登录页面
      router.push('/login'); 
      // return {data: {resultCode: 422, message: '缺少参数'}};
    }
    //仍然抛出错误
    return Promise.reject(error);
    //return {data: {resultCode: 500, message: '请求出错'}};
  }
);


// 请求拦截器（可选，为所有请求添加 token（如果有的话）
Axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default Axios;
