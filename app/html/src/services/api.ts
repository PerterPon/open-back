// API 服务层
// 用于与后端 Python 服务器通信

import { API_CONFIG } from '../constants';

// API 响应的通用格式
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
}

// Strategy 相关的类型定义
export interface Strategy {
  id: number;
  name: string;
  currency?: string;
  time_interval?: string;
  sharpe_ratio?: number;
  findal_balance?: number;
  max_drawdown?: number;
  trade_count?: number;
  total_commission?: number;
  winning_percetage?: number;
  init_balance?: number;
  reason?: string;
  extra?: string;
  created_at?: string;
  updated_at?: string;
}

export interface StrategyListResponse {
  strategies: Strategy[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
  sorting: {
    orderBy?: string;
    order: string;
  };
}

// 通用请求函数（内部使用）
const apiRequest = async <T = any>(
  endpoint: string,
  requestData?: any,
  options?: RequestInit
): Promise<ApiResponse<T>> => {
  try {
    const url = `${API_CONFIG.baseURL}${endpoint}`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      body: requestData ? JSON.stringify(requestData) : undefined,
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    return result as ApiResponse<T>;
  } catch (error) {
    console.error('API 请求失败：', error);
    throw error;
  }
};

/**
 * 通用的数据获取接口
 * @param method 方法名称，如 'getStrategy'
 * @param data 请求参数对象
 * @returns Promise<ApiResponse<T>> API 响应
 */
export const getData = async <T = any>(
  method: string,
  data: Record<string, any> = {}
): Promise<ApiResponse<T>> => {
  return apiRequest<T>('/api', {
    method,
    data,
  });
};

// Strategy API 方法（保留向后兼容性）
export const strategyApi = {
  // 获取策略列表
  getStrategies: async (params?: {
    page?: number;
    pageSize?: number;
    orderBy?: string;
    order?: 'asc' | 'desc';
  }): Promise<ApiResponse<StrategyListResponse>> => {
    return getData<StrategyListResponse>('getStrategy', params || {});
  },
};

// 导出默认 API 实例
export default {
  // 通用数据获取方法
  getData,
  
  // 专门的 API 方法（向后兼容）
  strategy: strategyApi,
};
