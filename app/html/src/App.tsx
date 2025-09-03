import React, { useEffect } from 'react';
import { RouterProvider } from 'react-router-dom';
import { ConfigProvider, theme, App as AntdApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import router from './router';
import { useSystemTheme } from './hooks/useSystemTheme';
import './App.css';

function App() {
  const systemTheme = useSystemTheme();
  
  // 根据系统主题配置 Ant Design 主题
  const antdTheme = {
    algorithm: systemTheme === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm,
    token: {
      colorPrimary: '#1890ff',
      borderRadius: 6,
      // 暗色主题下的特殊配置
      ...(systemTheme === 'dark' && {
        colorBgContainer: '#141414',
        colorBgElevated: '#1f1f1f',
        colorBorder: '#424242',
        colorText: '#ffffff',
        colorTextSecondary: '#a6a6a6',
      }),
    },
  };

  // 监听主题变化，更新页面标题
  useEffect(() => {
    const themeEmoji = systemTheme === 'dark' ? '🌙' : '☀️';
    document.title = `${themeEmoji} OpenBack Admin - ${systemTheme === 'dark' ? '暗色' : '亮色'}主题`;
    console.log('🎨 当前应用主题:', systemTheme);
  }, [systemTheme]);

  // 为body元素添加主题类名，方便自定义CSS
  useEffect(() => {
    const bodyClass = `theme-${systemTheme}`;
    document.body.className = bodyClass;
    
    return () => {
      document.body.className = '';
    };
  }, [systemTheme]);

  return (
    <ConfigProvider
      locale={zhCN}
      theme={antdTheme}
    >
      <AntdApp>
        <RouterProvider router={router} />
      </AntdApp>
    </ConfigProvider>
  );
}

export default App;
