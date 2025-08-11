# 离线数据收集器使用说明

本文档详细介绍了如何使用离线数据收集器来获取和管理加密货币的历史 K 线数据。

## 📁 文件结构

```
data-collector/
├── offline/
│   └── index.py          # 单个货币对数据收集器
├── get_offline.py         # 批量数据收集调度器
├── offline_readme.md      # 本文档
└── logs/                  # 日志文件目录
    └── offline_data_YYYYMMDD.log
```

## 🚀 快速开始

### 1. 环境准备

确保已安装必要的 Python 依赖：

```bash
pip3 install requests pymysql pyyaml
```

### 2. 数据库配置

确保 `config/default.yaml` 中的 MySQL 配置正确：

```yaml
mysql:
  host: your_host
  port: 3306
  username: your_username
  password: your_password
  database: your_database
```

## 📊 单个货币对数据收集

使用 `offline/index.py` 收集单个货币对的数据。

### 基本用法

```bash
# 收集 BTCUSDT 的 1 小时 K 线数据（默认最近 2 年）
python3 data-collector/offline/index.py --currency BTCUSDT --interval 1h

# 指定时间范围
python3 data-collector/offline/index.py --currency BTCUSDT --interval 1h --start-date 2024-01-01 --end-date 2024-12-31

# 显示详细日志
python3 data-collector/offline/index.py --currency BTCUSDT --interval 1h --verbose
```

### 参数说明

| 参数 | 短参数 | 必需 | 说明 | 示例 |
|------|--------|------|------|------|
| `--currency` | `-c` | ✅ | 货币对符号 | `BTCUSDT`, `ETHUSDT` |
| `--interval` | `-i` | ❌ | 时间间隔 | `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d` |
| `--start-date` | `-s` | ❌ | 开始日期 | `2024-01-01` |
| `--end-date` | `-e` | ❌ | 结束日期 | `2024-12-31` |
| `--verbose` | `-v` | ❌ | 显示详细日志 | - |

### 支持的时间间隔

- **分钟级别**: `1m`, `3m`, `5m`, `15m`, `30m`
- **小时级别**: `1h`, `2h`, `4h`, `6h`, `8h`, `12h`
- **日级别**: `1d`, `3d`
- **周/月级别**: `1w`, `1M`

### 示例命令

```bash
# 获取 BTCUSDT 最近一周的 1 小时数据
python3 data-collector/offline/index.py -c BTCUSDT -i 1h -s 2024-08-04 -e 2024-08-11

# 获取 ETHUSDT 的日线数据
python3 data-collector/offline/index.py -c ETHUSDT -i 1d -s 2023-01-01 -e 2024-01-01

# 获取 BNBUSDT 的 15 分钟数据（最近 30 天）
python3 data-collector/offline/index.py -c BNBUSDT -i 15m -s 2024-07-12 -e 2024-08-11
```

## 🔄 批量数据收集

使用 `get_offline.py` 批量收集多个货币对的数据。

### 基本用法

```bash
# 使用默认配置（10 个货币对，7 个时间间隔，最近 7 天）
python3 data-collector/get_offline.py

# 指定货币对和时间间隔
python3 data-collector/get_offline.py --currencies BTCUSDT ETHUSDT --intervals 1h 4h

# 指定时间范围
python3 data-collector/get_offline.py --start-date 2024-08-01 --end-date 2024-08-10

# 顺序执行（避免并发）
python3 data-collector/get_offline.py --sequential
```

### 参数说明

| 参数 | 短参数 | 说明 | 默认值 | 示例 |
|------|--------|------|--------|------|
| `--currencies` | `-c` | 指定货币对列表 | 预设 10 个主流币 | `BTCUSDT ETHUSDT` |
| `--intervals` | `-i` | 指定时间间隔列表 | 7 个常用间隔 | `1h 4h 1d` |
| `--days` | `-d` | 获取最近几天数据 | `7` | `30` |
| `--start-date` | `-s` | 开始日期 | 最近 N 天 | `2024-08-01` |
| `--end-date` | `-e` | 结束日期 | 今天 | `2024-08-10` |
| `--max-workers` | `-w` | 最大并发数 | `3` | `5` |
| `--sequential` | - | 顺序执行 | 并发执行 | - |
| `--verbose` | `-v` | 显示详细日志 | 简化日志 | - |

### 默认配置

**默认货币对列表**：
- BTCUSDT (比特币)
- ETHUSDT (以太坊)
- BNBUSDT (币安币)
- ADAUSDT (艾达币)
- XRPUSDT (瑞波币)
- SOLUSDT (Solana)
- DOTUSDT (波卡)
- DOGEUSDT (狗狗币)
- AVAXUSDT (雪崩)
- LINKUSDT (链链)

**默认时间间隔**：
- `1m` (1 分钟)
- `5m` (5 分钟)
- `15m` (15 分钟)
- `30m` (30 分钟)
- `1h` (1 小时)
- `4h` (4 小时)
- `1d` (1 天)

### 批量收集示例

```bash
# 收集主流币种最近一个月的小时级数据
python3 data-collector/get_offline.py \
  --currencies BTCUSDT ETHUSDT BNBUSDT ADAUSDT \
  --intervals 1h \
  --days 30 \
  --max-workers 2

# 收集特定时间段的多时间级别数据
python3 data-collector/get_offline.py \
  --currencies BTCUSDT ETHUSDT \
  --intervals 1h 4h 1d \
  --start-date 2024-07-01 \
  --end-date 2024-08-01 \
  --sequential

# 快速收集最近一周的数据（所有默认配置）
python3 data-collector/get_offline.py --days 7 --verbose
```

## 📈 数据收集策略

### 增量更新机制

系统会自动检查数据库中已有的数据，只获取缺失的部分：

1. **首次运行**：获取完整的时间范围数据
2. **再次运行**：只获取最新数据时间点之后的数据
3. **扩展范围**：自动计算并获取缺失的时间段

### 数据质量控制

- **收盘价验证**：自动过滤没有收盘价的无效数据
- **数据完整性**：确保 OHLCV 数据的完整性
- **重复数据处理**：数据库层面防止重复插入

### 性能优化

- **批量插入**：使用批量插入提高数据库写入效率
- **并发控制**：支持多线程并发，但限制并发数避免 API 限制
- **请求频率控制**：自动控制请求间隔，避免触发 API 限制

## 📝 日志和监控

### 日志文件

日志文件自动保存在 `data-collector/logs/` 目录下：

```
logs/
└── offline_data_20240811.log  # 按日期命名
```

### 日志内容

- **任务执行状态**：成功/失败状态
- **数据统计**：插入记录数、执行时间
- **错误信息**：详细的错误描述和堆栈信息
- **性能指标**：API 响应时间、数据库操作时间

### 执行结果摘要

批量收集完成后会显示详细的执行摘要：

```
============================================================
📊 执行结果摘要
============================================================
总任务数: 70
成功任务: 68
失败任务: 2
成功率: 97.1%
总插入记录数: 15420
总执行时间: 125.34s
平均执行时间: 1.79s/任务
============================================================
```

## 🔧 高级用法

### 定时任务配置

使用 cron 定时执行数据收集：

```bash
# 编辑 crontab
crontab -e

# 每天凌晨 2 点执行数据收集
0 2 * * * cd /path/to/open-back && python3 data-collector/get_offline.py --days 2 >> /var/log/kline_collection.log 2>&1

# 每小时执行一次增量更新
0 * * * * cd /path/to/open-back && python3 data-collector/get_offline.py --intervals 1h --days 1 >> /var/log/kline_hourly.log 2>&1
```

### 自定义货币对列表

创建自定义脚本：

```python
#!/usr/bin/env python3
import subprocess
import sys

# 自定义货币对
custom_currencies = ['BTCUSDT', 'ETHUSDT', 'MATICUSDT', 'LTCUSDT']
custom_intervals = ['1h', '4h', '1d']

# 执行批量收集
cmd = [
    'python3', 'data-collector/get_offline.py',
    '--currencies'] + custom_currencies + [
    '--intervals'] + custom_intervals + [
    '--days', '30',
    '--max-workers', '2'
]

subprocess.run(cmd)
```

### 数据验证脚本

验证收集的数据：

```python
#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
from core.mysql.kline import get_klines_by_currency_time_interval

currencies = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
intervals = ['1h', '4h', '1d']

print("=== 数据收集状态检查 ===")
for currency in currencies:
    print(f"\n{currency}:")
    for interval in intervals:
        count = len(get_klines_by_currency_time_interval(currency, interval, 10000))
        if count > 0:
            latest = get_klines_by_currency_time_interval(currency, interval, 1)[0]
            print(f"  {interval}: {count:,} 条记录 (最新：{latest['time']})")
        else:
            print(f"  {interval}: 无数据")
```

## ❗ 注意事项

### API 限制

- **请求频率**：Binance API 有请求频率限制，建议不要设置过高的并发数
- **数据量限制**：单次请求最多返回 1000 条数据，系统会自动分批处理
- **网络稳定性**：确保网络连接稳定，避免请求超时

### 数据库性能

- **批量插入**：大量数据建议使用批量模式
- **索引优化**：确保数据库表有适当的索引
- **存储空间**：注意监控数据库存储空间使用情况

### 系统资源

- **内存使用**：大量数据处理时注意内存使用情况
- **磁盘空间**：日志文件和数据库文件会占用磁盘空间
- **CPU 使用**：并发处理会增加 CPU 使用率

## 🐛 故障排除

### 常见错误

1. **网络连接错误**
   ```
   请求 Binance API 失败：HTTPSConnectionPool...
   ```
   **解决方案**：检查网络连接，考虑使用代理或重试

2. **数据库连接错误**
   ```
   连接 MySQL 数据库失败：(2003, "Can't connect to MySQL server...")
   ```
   **解决方案**：检查数据库配置和网络连接

3. **权限错误**
   ```
   [Errno 13] Permission denied: 'data-collector/logs/...'
   ```
   **解决方案**：确保有写入日志目录的权限

### 调试技巧

1. **使用详细日志**：添加 `--verbose` 参数查看详细执行过程
2. **单个任务测试**：先用单个货币对测试，确认配置正确
3. **检查日志文件**：查看日志文件了解详细的错误信息
4. **数据库验证**：使用 SQL 直接查询验证数据是否正确插入

## 📞 技术支持

如果遇到问题，可以：

1. 查看日志文件获取详细错误信息
2. 检查网络连接和数据库配置
3. 使用 `--verbose` 参数获取更多调试信息
4. 确认 Binance API 的可用性和限制

---

**最后更新时间**: 2024-08-11  
**版本**: 1.0.0
