# API 使用指南

## 🎯 getData 接口说明

新的 `getData` 接口提供了统一、简洁的API调用方式。

### 📋 接口签名

```typescript
getData<T = any>(
  method: string,
  data: Record<string, any> = {}
): Promise<ApiResponse<T>>
```

### 🔥 使用示例

#### 1. 基本用法

```typescript
import { getData } from './services/api';

// 获取策略列表 - 默认参数
const response = await getData('getStrategy');
```

#### 2. 带参数调用

```typescript
// 获取策略列表 - 自定义参数
const response = await getData('getStrategy', {
  page: 1,
  pageSize: 10,
  orderBy: 'sharpe_ratio',
  order: 'desc'
});

// 检查响应
if (response.success) {
  const strategies = response.data.strategies;
  const pagination = response.data.pagination;
  console.log(`获取到 ${strategies.length} 条策略，总共 ${pagination.total} 条`);
} else {
  console.error('API调用失败:', response.message);
}
```

#### 3. 在React组件中使用

```typescript
import React, { useState, useEffect } from 'react';
import { getData } from '../services/api';

const StrategyList: React.FC = () => {
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchStrategies = async () => {
    setLoading(true);
    try {
      const response = await getData('getStrategy', {
        page: 1,
        pageSize: 20,
        orderBy: 'sharpe_ratio',
        order: 'desc'
      });
      
      if (response.success) {
        setStrategies(response.data.strategies);
      } else {
        console.error('获取策略失败:', response.message);
      }
    } catch (error) {
      console.error('请求异常:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStrategies();
  }, []);

  return (
    <div>
      {loading ? '加载中...' : `共 ${strategies.length} 条策略`}
    </div>
  );
};
```

#### 4. 错误处理

```typescript
try {
  const response = await getData('getStrategy', {
    page: 1,
    pageSize: 10
  });
  
  if (response.success) {
    // 处理成功响应
    console.log('数据:', response.data);
  } else {
    // 处理业务错误
    console.error('业务错误:', response.message);
  }
} catch (error) {
  // 处理网络错误或其他异常
  console.error('请求异常:', error);
}
```

## 🔄 支持的方法

目前支持的方法：

| 方法名 | 说明 | 参数 |
|--------|------|------|
| `getStrategy` | 获取策略列表 | `page`, `pageSize`, `orderBy`, `order` |

### getStrategy 参数详解

```typescript
interface GetStrategyParams {
  page?: number;        // 页码，默认1
  pageSize?: number;    // 每页数量，默认20，最大100
  orderBy?: string;     // 排序字段：sharpe_ratio, findal_balance, max_drawdown, trade_count, total_commission, winning_percetage
  order?: 'asc' | 'desc'; // 排序方向，默认asc
}

// 使用示例
await getData('getStrategy', {
  page: 1,
  pageSize: 10,
  orderBy: 'sharpe_ratio',
  order: 'desc'
});
```

## 🎨 响应格式

所有API响应都遵循统一格式：

```typescript
interface ApiResponse<T> {
  success: boolean;     // 请求是否成功
  message: string;      // 错误信息（成功时为空字符串）
  data: T;             // 具体返回数据
}
```

### getStrategy 响应示例

```json
{
  "success": true,
  "message": "",
  "data": {
    "strategies": [
      {
        "id": 4785,
        "name": "策略名称",
        "currency": "ETHUSDT",
        "sharpe_ratio": 0.2151,
        "findal_balance": 10106.48,
        "trade_count": 1,
        "winning_percetage": 1.0,
        "created_at": "2025-09-03T11:13:51"
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 10,
      "total": 7066,
      "totalPages": 707,
      "hasNext": true,
      "hasPrev": false
    },
    "sorting": {
      "orderBy": "sharpe_ratio",
      "order": "desc"
    }
  }
}
```

## 🔧 高级用法

### 1. 类型安全调用

```typescript
import { StrategyListResponse } from './services/api';

// 指定返回类型
const response = await getData<StrategyListResponse>('getStrategy', {
  page: 1,
  pageSize: 10
});

// TypeScript 会提供完整的类型提示
const strategies = response.data.strategies; // 类型安全
```

### 2. 自定义请求选项

```typescript
// getData 内部使用 fetch，支持所有 fetch 选项
const response = await getData('getStrategy', {
  page: 1,
  pageSize: 10
});
```

### 3. 并发请求

```typescript
// 同时获取多页数据
const [page1, page2, page3] = await Promise.all([
  getData('getStrategy', { page: 1, pageSize: 10 }),
  getData('getStrategy', { page: 2, pageSize: 10 }),
  getData('getStrategy', { page: 3, pageSize: 10 })
]);
```

## 🛠️ 开发建议

1. **优先使用 getData** - 新代码建议使用通用的 getData 接口
2. **保持向后兼容** - 现有代码可以继续使用专门的API方法
3. **类型安全** - 使用 TypeScript 类型注解获得更好的开发体验
4. **错误处理** - 始终检查 `response.success` 字段
5. **性能优化** - 合理使用分页，避免一次获取过多数据

## 🧪 测试工具

项目提供了多个测试工具：

1. **`test/getData-test.html`** - 浏览器端测试页面
2. **`test/api-test.ts`** - TypeScript 测试用例
3. **`test/cors-test.html`** - CORS 跨域功能测试

这些工具可以帮助你验证API功能和调试问题。
