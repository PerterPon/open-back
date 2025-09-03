// 常量定义文件

// 应用配置
export const APP_CONFIG = {
  title: 'OpenBack 策略管理系统',
  version: '1.0.0',
  description: '专业的量化交易策略管理平台',
};

// API 配置
export const API_CONFIG = {
  baseURL: 'http://localhost:8081',
  timeout: 10000,
};

// 路由路径
export const ROUTES = {
  HOME: '/',
  STRATEGY: '/strategy',
  SETTINGS: '/settings',
};

// 菜单配置
export const MENU_ITEMS = [
  {
    key: ROUTES.HOME,
    label: '首页',
    icon: 'HomeOutlined',
  },
  {
    key: ROUTES.STRATEGY,
    label: '策略管理',
    icon: 'BarChartOutlined',
  },
  {
    key: ROUTES.SETTINGS,
    label: '系统设置',
    icon: 'SettingOutlined',
  },
];
