# 🎨 Strategy 表格颜色标识说明

## 功能概览

Strategy 页面的表格现在支持**智能颜色标识**，通过红绿色直观显示策略的关键指标表现。

## 🎯 颜色标识规则

### 1. 胜率 (Winning Percentage) 📈
- **🟢 绿色**: 胜率 > 50%（表现良好）
- **🔴 红色**: 胜率 ≤ 50%（需要改进）

```typescript
// 判断逻辑
const percentage = value * 100;
const isGood = percentage > 50;
```

### 2. 最大回撤 (Max Drawdown) 📉
- **🟢 绿色**: 回撤 < 30%（风险控制良好）
- **🔴 红色**: 回撤 ≥ 30%（风险较高）

```typescript
// 判断逻辑
const isGood = value < 0.3; // 小于30%
```

### 3. 最终余额 (Final Balance) 💰
- **🟢 绿色**: 最终余额 > 初始余额（盈利）
- **🔴 红色**: 最终余额 ≤ 初始余额（亏损）

```typescript
// 判断逻辑
const isProfit = finalBalance > initBalance;
```

## 🎨 视觉效果

### 颜色配置
- **成功色**: `#52c41a` (Ant Design 绿色)
- **失败色**: `#f5222d` (Ant Design 红色)
- **字体粗细**: `bold` (加粗显示)

### 主题适配
支持亮色/暗色主题自动切换：
- **亮色主题**: 使用标准的绿色 `#52c41a` 和红色 `#f5222d`
- **暗色主题**: 使用适配的绿色 `#73d13d` 和红色 `#ff7875`

## 📊 实际数据示例

基于当前API数据的颜色效果：

```
策略示例:
📈 胜率: 21.43% 🔴 (低于50%，显示红色)
📉 回撤: 0.0126 🟢 (低于30%，显示绿色) 
💰 余额: 10073.20 vs 10000.00 🟢 (盈利，显示绿色)
```

## 🔧 技术实现

### 核心代码

```typescript
// 1. 导入颜色工具函数
import { getStrategyFieldColor } from '../../constants/colors';

// 2. 获取主题信息
const { token } = theme.useToken();
const isDarkTheme = token.colorBgContainer === '#141414';

// 3. 表格列渲染配置
{
  title: 'Winning Percentage',
  render: (value: number) => {
    const color = getStrategyFieldColor('winning_percentage', value, undefined, isDarkTheme);
    return (
      <span style={{ color, fontWeight: 'bold' }}>
        {(value * 100).toFixed(2)}%
      </span>
    );
  },
}
```

### 颜色工具函数

```typescript
// constants/colors.ts
export const getStrategyFieldColor = (
  field: 'winning_percentage' | 'max_drawdown' | 'final_balance',
  value: number,
  compareValue?: number,
  isDark: boolean = false
) => {
  const colors = getThemeColors(isDark);
  
  switch (field) {
    case 'winning_percentage':
      return (value * 100) > 50 ? colors.success : colors.error;
    case 'max_drawdown':
      return value < 0.3 ? colors.success : colors.error;
    case 'final_balance':
      return compareValue !== undefined && value > compareValue 
        ? colors.success : colors.error;
    default:
      return colors.neutral;
  }
};
```

## 🎯 用户体验优势

### 1. 直观识别
- **一目了然**: 通过颜色快速识别策略表现
- **减少认知负担**: 无需计算比较，颜色直接传达信息
- **提高效率**: 快速筛选出表现良好的策略

### 2. 专业标准
- **金融行业惯例**: 绿色代表盈利/良好，红色代表亏损/风险
- **国际化**: 颜色语言通用，无需文字说明

### 3. 响应式设计
- **主题适配**: 颜色在亮色/暗色主题下都有良好的对比度
- **可访问性**: 除了颜色还使用粗体，确保可读性

## 📱 使用场景

### 策略筛选
- **快速找到高胜率策略**: 寻找绿色的胜率列
- **风险控制评估**: 查看回撤列的颜色分布
- **盈利策略识别**: 关注绿色的最终余额

### 数据分析
- **整体表现评估**: 通过颜色分布了解策略质量
- **风险收益平衡**: 综合查看三个指标的颜色组合
- **策略对比**: 不同策略间的视觉对比更加直观

## 🧪 测试验证

### 测试数据验证
根据实际API数据测试：
- ✅ 胜率21.43% → 🔴 红色（< 50%）
- ✅ 回撤0.0126 → 🟢 绿色（< 30%）  
- ✅ 余额10073.20 vs 10000.00 → 🟢 绿色（盈利）

### 边界值测试
- 胜率50%：红色（≤ 50%）
- 胜率50.01%：绿色（> 50%）
- 回撤30%：红色（≥ 30%）
- 回撤29.99%：绿色（< 30%）

## 🚀 访问和使用

1. **启动应用**:
   ```bash
   # 后端
   cd app/server && python3 start_server.py
   
   # 前端  
   cd app/html && npm start
   ```

2. **查看效果**:
   - 访问: `http://localhost:3000/strategy`
   - 观察表格中的红绿色字段
   - 测试排序功能，颜色会保持正确

3. **演示页面**:
   - 颜色演示: `src/test/color-demo.html`
   - 功能测试: 在浏览器中直接查看颜色效果

## 💡 开发建议

### 扩展颜色规则
如需添加更多字段的颜色标识：

```typescript
// 在 constants/colors.ts 中扩展
case 'sharpe_ratio':
  return value > 1.0 ? colors.success : colors.error;
```

### 自定义颜色
可以在 `constants/colors.ts` 中调整颜色值：

```typescript
export const COLORS = {
  SUCCESS: '#52c41a',  // 可以改为其他绿色
  ERROR: '#f5222d',    // 可以改为其他红色
  // ...
};
```

现在你的Strategy表格具有了专业的颜色标识功能，可以帮助用户快速识别策略的关键表现指标！
