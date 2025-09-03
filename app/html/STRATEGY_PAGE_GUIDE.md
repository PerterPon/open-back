# Strategy 页面使用指南

## 🎯 功能概览

Strategy 页面是一个完整的策略管理界面，提供了数据展示、分页、排序等核心功能。

## ✨ 主要功能

### 📊 数据展示
- **自动加载**: 页面加载后自动获取第一页数据（50条/页）
- **表格展示**: 使用 Ant Design Table 组件展示策略数据
- **响应式**: 支持横向滚动，适配不同屏幕尺寸

### 📋 表格字段

根据数据库表结构，展示以下字段：

| 字段 | 说明 | 格式 |
|------|------|------|
| Name | 策略名称 | 文本，支持省略号 |
| Currency | 交易货币对 | 文本 |
| Time Interval | 时间间隔 | 文本 |
| **Sharpe Ratio** | 夏普比率 | 数字，6位小数，支持排序 |
| **Final Balance** | 最终余额 | 数字，2位小数，支持排序 |
| **Max Drawdown** | 最大回撤 | 数字，6位小数，支持排序 |
| **Trade Count** | 交易次数 | 整数，支持排序 |
| **Total Commission** | 总手续费 | 数字，2位小数，支持排序 |
| Winning Percentage | 胜率 | 百分比格式 |
| Init Balance | 初始余额 | 数字，2位小数 |
| Created At | 创建时间 | 本地化时间格式 |
| Updated At | 更新时间 | 本地化时间格式 |

**注意**: 粗体字段支持点击排序

### 📄 分页功能

- **默认设置**: 第1页，每页50条
- **页面选项**: 20、50、100、200条/页
- **快速跳转**: 支持直接输入页码跳转
- **统计信息**: 显示当前页范围和总记录数

### 🔄 排序功能

支持以下字段的正序/倒序排序：
- `sharpe_ratio` - 夏普比率
- `findal_balance` - 最终余额  
- `max_drawdown` - 最大回撤
- `trade_count` - 交易次数
- `total_commission` - 总手续费

**排序行为**:
- 点击列标题进行排序
- 每次排序都会重新请求API
- 默认正序，再次点击切换为倒序
- 第三次点击取消排序

## 🔧 技术实现

### API 调用

页面使用新的 `getData` 接口：

```typescript
// 基本调用
const response = await getData<StrategyResponse>('getStrategy', {
  page: 1,
  pageSize: 50
});

// 带排序的调用
const response = await getData<StrategyResponse>('getStrategy', {
  page: 1,
  pageSize: 50,
  orderBy: 'sharpe_ratio',
  order: 'desc'
});
```

### 状态管理

```typescript
const [strategies, setStrategies] = useState<StrategyData[]>([]);
const [loading, setLoading] = useState<boolean>(false);
const [pagination, setPagination] = useState<PaginationInfo>({
  page: 1,
  pageSize: 50,
  total: 0,
  totalPages: 0,
  hasNext: false,
  hasPrev: false
});
```

### 事件处理

```typescript
const handleTableChange: TableProps<StrategyData>['onChange'] = (paginationConfig, filters, sorter) => {
  // 处理分页和排序变化
  // 自动调用API获取新数据
};
```

## 🎨 UI 特性

- **加载状态**: 请求数据时显示 Spinner
- **错误处理**: 网络错误或API错误时显示 message 提示
- **数据格式化**: 数字字段自动格式化显示
- **时间本地化**: 时间字段显示为中文格式
- **表格优化**: 小尺寸表格，带边框，水平滚动

## 🚀 访问方式

1. **启动服务器**:
   ```bash
   # 后端
   cd app/server && python3 start_server.py

   # 前端
   cd app/html && npm start
   ```

2. **访问页面**:
   - 打开浏览器访问: `http://localhost:3000`
   - 点击左侧导航栏的 "策略管理" 菜单

## 📱 使用流程

1. **页面加载** → 自动获取第一页数据（50条）
2. **查看数据** → 表格展示所有策略字段
3. **分页浏览** → 使用底部分页器切换页面
4. **排序查看** → 点击支持排序的列标题进行排序
5. **调整页面大小** → 使用分页器改变每页显示条数

## 🛠️ 开发说明

### 数据流
1. 页面加载 → `useEffect` 触发
2. 调用 `fetchStrategies` → 使用 `getData` 接口
3. API响应 → 更新 `strategies` 和 `pagination` 状态
4. 表格重新渲染 → 显示最新数据

### 扩展点
- **新增字段**: 在 `columns` 数组中添加新列定义
- **新增排序**: 在 `sortableFields` 数组中添加字段名
- **自定义格式**: 修改 `render` 函数改变字段显示格式
- **筛选功能**: 可以添加 `filters` 配置实现字段筛选

这个页面完全符合你的要求，提供了完整的策略数据管理功能！
