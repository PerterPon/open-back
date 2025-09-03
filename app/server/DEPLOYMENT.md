# 部署说明

## 🌐 服务器部署

这个HTTP服务器已经优化为可移植版本，可以在任意Linux/Unix/macOS服务器上运行。

### 📋 部署前准备

1. **Python环境**: 确保服务器上安装了Python 3.7+
2. **项目文件**: 将整个 `open-back` 项目上传到服务器
3. **权限设置**: 确保有文件读写权限

### 🚀 快速部署

1. **上传项目文件到服务器**
   ```bash
   # 使用scp或其他方式上传项目到服务器
   scp -r open-back/ user@server:/path/to/your/project/
   ```

2. **进入服务器目录**
   ```bash
   ssh user@server
   cd /path/to/your/project/open-back/app/server
   ```

3. **安装依赖**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

4. **启动服务器**
   ```bash
   # 方法1：使用启动脚本（推荐）
   chmod +x run.sh
   ./run.sh

   # 方法2：直接运行
   python3 main.py

   # 方法3：后台运行
   nohup python3 main.py > server.log 2>&1 &
   ```

### 🔧 配置修改

- **端口配置**: 修改 `config/default.yaml` 中的 `server.port` 值
- **数据库配置**: 同样在 `config/default.yaml` 中修改mysql相关配置

### 🐳 Docker 部署（可选）

你也可以创建Dockerfile来容器化部署：

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . /app/

RUN pip install -r app/server/requirements.txt

EXPOSE 8081

CMD ["python3", "app/server/main.py"]
```

### 🔍 部署验证

部署完成后，可以通过以下方式验证：

```bash
# 检查服务器状态
curl -X GET http://your-server-ip:8081/api/health

# 测试主要接口
curl -X POST http://your-server-ip:8081/test \
  -H "Content-Type: application/json" \
  -d '{"test": "server deployment"}'
```

### 🛠️ 故障排除

1. **端口被占用**: 修改 `config/default.yaml` 中的端口号
2. **导入错误**: 确保项目根目录结构完整
3. **权限问题**: 检查文件和目录权限设置
4. **依赖问题**: 确保所有Python包都正确安装

### 📊 监控和日志

- 服务器日志会输出到标准输出
- 使用 `nohup` 运行时，日志保存到 `server.log` 文件
- 可以通过 `/api/health` 接口监控服务器状态
