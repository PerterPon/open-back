# 🎨 主题系统使用指南

## 功能概览

前端应用现在支持**自动跟随系统主题**，使用Ant Design的主题算法实现亮色/暗色主题的无缝切换。

## ✨ 主要特性

### 🔄 自动主题检测
- **系统跟随**: 自动检测操作系统的主题设置
- **实时切换**: 系统主题变化时应用立即响应
- **无需配置**: 用户无需手动设置，完全自动化

### 🎯 支持的主题
- **亮色主题** ☀️: 使用 Ant Design 默认算法
- **暗色主题** 🌙: 使用 Ant Design 暗色算法

### 🚀 技术实现

#### 1. 自定义Hook - `useSystemTheme`

```typescript
import { useSystemTheme } from './hooks/useSystemTheme';

const systemTheme = useSystemTheme(); // 'light' | 'dark'
```

**功能:**
- 初始化时检测系统主题
- 监听 `prefers-color-scheme` 媒体查询变化
- 返回当前主题状态

#### 2. App.tsx 配置

```typescript
const antdTheme = {
  algorithm: systemTheme === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
    // 暗色主题特殊配置
    ...(systemTheme === 'dark' && {
      colorBgContainer: '#141414',
      colorBgElevated: '#1f1f1f',
      colorBorder: '#424242',
      colorText: '#ffffff',
      colorTextSecondary: '#a6a6a6',
    }),
  },
};
```

#### 3. CSS 主题支持

自动为 `<body>` 元素添加主题类名：
- 亮色主题: `theme-light`
- 暗色主题: `theme-dark`

## 🎨 主题效果

### 亮色主题 ☀️
- **背景**: 白色和浅灰色
- **文字**: 深色文字
- **边框**: 浅灰色边框
- **组件**: Ant Design 默认样式

### 暗色主题 🌙
- **背景**: 深灰色和黑色
- **文字**: 白色和浅色文字
- **边框**: 深灰色边框
- **组件**: Ant Design 暗色样式

## 🔧 组件适配

### 表格组件
```css
/* 暗色主题下的表格优化 */
.theme-dark .ant-table {
  background: transparent;
}

.theme-dark .ant-table-thead > tr > th {
  background: rgba(255, 255, 255, 0.04);
  border-bottom: 1px solid #424242;
}
```

### 布局组件
- **侧边栏**: 自动使用深色菜单主题
- **顶部栏**: 根据主题调整背景和边框颜色
- **内容区**: 使用 Ant Design 的 `colorBgContainer` token

## 🧪 测试方法

### 1. 系统主题切换测试

**macOS:**
1. 打开 "系统偏好设置"
2. 选择 "通用"
3. 在 "外观" 中选择 "浅色" 或 "深色"
4. 观察React应用的主题变化

**Windows:**
1. 打开 "设置"
2. 选择 "个性化" → "颜色"
3. 在 "选择应用模式" 中选择 "浅色" 或 "深色"

### 2. 浏览器开发者工具测试

1. 打开开发者工具 (F12)
2. 点击 "更多工具" → "渲染"
3. 找到 "模拟CSS媒体功能"
4. 设置 `prefers-color-scheme` 为 `dark` 或 `light`

### 3. 测试页面

访问 `src/test/theme-test.html` 进行独立测试：
```bash
# 在浏览器中打开
open src/test/theme-test.html
```

## 🔍 调试信息

应用会在浏览器控制台输出主题变化日志：

```
🎨 当前应用主题: light
🎨 系统主题已切换到: dark
```

页面标题也会显示当前主题状态：
- `☀️ OpenBack Admin - 亮色主题`
- `🌙 OpenBack Admin - 暗色主题`

## 📱 使用体验

### 自动化体验
- **无感切换**: 用户切换系统主题时，应用立即跟随
- **一致性**: 与系统其他应用保持视觉一致
- **性能**: 主题切换使用CSS过渡动画，体验流畅

### 开发友好
- **类型安全**: 完整的TypeScript类型支持
- **易扩展**: 可以轻松添加新的主题token配置
- **调试便利**: 控制台日志帮助调试主题问题

## 🚀 启动和访问

1. **启动应用**:
   ```bash
   cd app/html
   npm start
   ```

2. **访问地址**: `http://localhost:3000`

3. **测试主题**: 更改系统主题设置，观察应用变化

## 🛠️ 扩展开发

### 添加自定义主题token

```typescript
// 在 App.tsx 中扩展主题配置
const antdTheme = {
  algorithm: systemTheme === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
    // 自定义token
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#f5222d',
  },
};
```

### 添加主题相关的CSS

```css
/* 在组件CSS中添加主题特定样式 */
.theme-light .my-component {
  background: #ffffff;
  color: #333333;
}

.theme-dark .my-component {
  background: #1f1f1f;
  color: #ffffff;
}
```

这个主题系统为你的应用提供了现代化的用户体验，完全跟随系统设置，无需用户手动配置！
