import axios from 'axios';
import { AuthResponse, AssetsResponse, Asset } from '../types';

const API_BASE_URL = '/api';

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 自动添加 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器 - 处理未授权错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 认证 API
export const authAPI = {
  register: async (email: string, username: string, password: string) => {
    const response = await api.post<AuthResponse>('/auth/register', {
      email,
      username,
      password,
    });
    return response.data;
  },

  login: async (emailOrUsername: string, password: string) => {
    const response = await api.post<AuthResponse>('/auth/login', {
      emailOrUsername,
      password,
    });
    return response.data;
  },
};

// 资产 API
export const assetAPI = {
  getAssets: async () => {
    const response = await api.get<AssetsResponse>('/assets');
    return response.data;
  },

  addAsset: async (symbol: string, name: string, type: string, notes?: string) => {
    const response = await api.post<{ message: string; asset: Asset }>('/assets', {
      symbol,
      name,
      type,
      notes,
    });
    return response.data;
  },

  updateAsset: async (id: number, data: { name?: string; type?: string; notes?: string }) => {
    const response = await api.put<{ message: string; asset: Asset }>(`/assets/${id}`, data);
    return response.data;
  },

  deleteAsset: async (id: number) => {
    const response = await api.delete<{ message: string }>(`/assets/${id}`);
    return response.data;
  },
};

export default api;
