import { useState, useEffect } from 'react';

export type ThemeMode = 'light' | 'dark';

/**
 * 检测和监听系统主题变化的 Hook
 * @returns 当前主题模式 ('light' | 'dark')
 */
export const useSystemTheme = (): ThemeMode => {
  const [theme, setTheme] = useState<ThemeMode>(() => {
    // 初始化时检测系统主题
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'light'; // 默认亮色主题
  });

  useEffect(() => {
    // 检查浏览器是否支持 matchMedia
    if (typeof window === 'undefined' || !window.matchMedia) {
      return;
    }

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    // 主题变化处理函数
    const handleThemeChange = (e: MediaQueryListEvent) => {
      const newTheme = e.matches ? 'dark' : 'light';
      setTheme(newTheme);
      console.log('🎨 系统主题已切换到:', newTheme);
    };

    // 添加监听器
    mediaQuery.addEventListener('change', handleThemeChange);

    // 设置初始主题
    setTheme(mediaQuery.matches ? 'dark' : 'light');

    // 清理函数
    return () => {
      mediaQuery.removeEventListener('change', handleThemeChange);
    };
  }, []);

  return theme;
};

/**
 * 手动切换主题的 Hook（可选功能）
 * @returns [currentTheme, toggleTheme]
 */
export const useThemeToggle = (): [ThemeMode, () => void] => {
  const [theme, setTheme] = useState<ThemeMode>('light');

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    console.log('🔄 手动切换主题到:', newTheme);
  };

  return [theme, toggleTheme];
};
