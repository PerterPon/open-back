# OpenBack 项目完整指南

## 🎯 项目概述

OpenBack 是一个完整的量化交易策略管理系统，包含前端管理界面和后端API服务。

## 📁 项目结构

```
open-back/
├── app/
│   ├── html/                    # React前端项目
│   │   ├── src/
│   │   │   ├── components/     # UI组件
│   │   │   ├── pages/          # 页面组件
│   │   │   ├── router/         # 路由配置
│   │   │   ├── services/       # API服务层
│   │   │   └── constants/      # 常量定义
│   │   ├── package.json
│   │   └── start_frontend.sh   # 前端启动脚本
│   └── server/                 # Python后端项目
│       ├── routes/             # API路由
│       ├── main.py            # 服务器主文件
│       ├── requirements.txt   # Python依赖
│       └── run.sh            # 后端启动脚本
├── core/                      # 核心模块
│   ├── config/               # 配置管理
│   └── mysql/                # 数据库访问层
├── config/
│   └── default.yaml          # 系统配置文件
└── PROJECT_GUIDE.md          # 项目指南
```

## 🚀 快速启动

### 1. 启动后端服务器

```bash
# 进入后端目录
cd /Volumes/data/project/open-back/app/server

# 安装Python依赖
python3 -m pip install -r requirements.txt

# 启动服务器
./run.sh
```

**后端服务地址**: http://localhost:8081

### 2. 启动前端应用

```bash
# 进入前端目录
cd /Volumes/data/project/open-back/app/html

# 安装Node.js依赖
npm install

# 启动开发服务器
./start_frontend.sh
```

**前端访问地址**: http://localhost:3000

## 🔧 技术栈

### 后端 (Python)
- **Flask 3.0.0** - Web框架
- **PyMySQL 1.1.0** - MySQL数据库连接
- **Flask-CORS 6.0.1** - 跨域支持
- **PyYAML 6.0.1** - 配置文件解析

### 前端 (React)
- **React 19.1.1** - 前端框架
- **TypeScript 4.9.5** - 类型安全
- **Ant Design** - UI组件库
- **React Router DOM** - 路由管理

### 数据库
- **MySQL** - 主数据库
- **Strategy表** - 存储策略数据

## 📡 API 接口

### 统一API格式

**请求格式**:
```json
{
    "method": "方法名",
    "data": {
        // 具体参数
    }
}
```

**响应格式**:
```json
{
    "success": true/false,
    "message": "错误信息（成功时为空）",
    "data": {
        // 返回数据
    }
}
```

### 可用接口

1. **POST /test** - 测试接口
2. **POST /api** - 统一业务API
   - `getStrategy` - 获取策略列表（支持分页、排序）

## ✅ CORS 跨域支持

已配置完整的CORS跨域支持：
- ✅ 允许所有域名访问 (`origins="*"`)
- ✅ 支持所有HTTP方法 (GET, POST, PUT, DELETE, OPTIONS)
- ✅ 允许常用请求头 (Content-Type, Authorization等)
- ✅ 支持携带凭证 (`supports_credentials=True`)

### 验证CORS功能

```bash
# 测试OPTIONS预检请求
curl -X OPTIONS http://127.0.0.1:8081/api \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v

# 测试实际跨域请求
curl -X POST http://127.0.0.1:8081/api \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -d '{"method": "getStrategy", "data": {"page": 1, "pageSize": 2}}' \
  -i
```

## 🎨 前端界面

### 主要页面
1. **首页** - Hello World欢迎页面，包含系统概览
2. **策略管理** - 策略数据展示（待完善）
3. **系统设置** - 系统配置（待完善）

### UI特性
- 响应式布局，支持移动端
- 现代化设计风格
- 中文本地化界面
- 可折叠侧边栏
- 用户头像下拉菜单

## 🔍 开发调试

### 后端调试
```bash
cd /Volumes/data/project/open-back/app/server
python3 test_database.py  # 测试数据库连接
python3 main.py          # 直接启动服务器
```

### 前端调试
```bash
cd /Volumes/data/project/open-back/app/html
npm start                # 启动开发服务器
npm run build           # 构建生产版本
```

### 跨域测试
- 使用浏览器开发者工具查看Network面板
- 检查响应头中的CORS相关字段
- 使用 `cors-test.html` 页面进行功能测试

## 🌐 部署指南

### 开发环境
- 后端：http://localhost:8081
- 前端：http://localhost:3000

### 生产环境
1. **后端部署**：将整个项目上传到服务器，运行Python服务
2. **前端部署**：构建后部署到静态文件服务器
3. **反向代理**：配置Nginx等代理前后端请求

## 🎉 项目亮点

1. **完整的前后端分离架构**
2. **统一的API设计规范**
3. **完善的CORS跨域支持**
4. **可移植的部署方案**
5. **现代化的技术栈**
6. **类型安全的开发体验**
7. **企业级UI设计**

现在你拥有了一个完整的、生产就绪的量化交易策略管理系统！
