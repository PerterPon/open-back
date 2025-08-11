# 加密货币交易策略回测系统

## 概述

这是一个基于 backtrader 框架的专业加密货币交易策略回测系统。系统从 MySQL 数据库读取 K 线数据，动态加载策略文件，执行回测并计算各种性能指标。

### 主要特性

- 🚀 **高精度计算**：使用 backtrader 内置分析器确保指标计算准确性
- 📊 **动态时间框架**：根据数据间隔自动设置分析器参数
- 🔧 **灵活配置**：支持多种时间间隔（1m-1M）和策略动态加载
- 📈 **全面指标**：夏普比率、最大回撤、Calmar 比率、VWR 等专业指标
- 🎯 **易于扩展**：模块化设计，支持自定义策略和分析器

## 文件结构

```
back-test/
├── index.py                      # 主回测引擎
├── README.md                     # 使用说明文档
├── requirements.txt              # Python依赖包
├── ANALYZER_CONFIGURATION.md    # 分析器配置说明
└── strategy/                     # 策略文件夹
    ├── simple_ma.py             # 简单移动平均策略
    ├── rsi_ma.py                # RSI + 移动平均策略
    ├── buy_hold.py              # 买入持有策略
    └── test_predictable.py      # 可预测测试策略
```

## 使用方法

### 基本用法

```bash
python index.py --currency BTCUSDT --time_interval 1h --strategy_name simple_ma
```

### 参数说明

- `--currency`: 货币对，如 BTCUSDT、ETHUSDT 等
- `--time_interval`: 时间间隔，支持格式：
  - **分钟级**：1m, 5m, 15m, 30m
  - **小时级**：1h, 2h, 4h, 6h, 8h, 12h
  - **日级**：1d, 1D
  - **周级**：1w, 1W
  - **月级**：1M（注意大写）
- `--strategy_name`: 策略名称，对应 strategy 文件夹下的 Python 文件名（无需 .py 后缀）

### 输出格式

系统会输出 JSON 格式的回测结果：

```json
{
  "currency": "BTCUSDT",
  "time_interval": "4h",
  "sharpe_ratio": 0.024432065173515156,
  "trade_count": 45,
  "trades": [
    {
      "time": "2024-08-28 04:00:00",
      "balance": 10423.171931051264,
      "price": 59337.41,
      "size": 0.0,
      "pnl": 442.61454239163027,
      "pnlcomm": 423.1719310512653,
      "commission": 19.442611340364987
    }
  ],
  "total_commission": 1121.37,
  "max_drawdown": 0.28259016548838395,
  "winning_percentage": 0.4,
  "init_balance": 10000.0,
  "final_balance": 13734.44,
  "total_return": 0.3734,
  "annual_return": 0.4112576108437447,
  "calmar_ratio": 0.0,
  "vwr": 11.531614960717375,
  "data_points": 2189,
  "start_date": "2024-08-09 00:00:00",
  "end_date": "2025-08-11 00:00:00"
}
```

### 字段说明

#### 基础信息
- `currency`: 货币对
- `time_interval`: 时间间隔
- `data_points`: 数据点数量
- `start_date`: 回测开始日期
- `end_date`: 回测结束日期

#### 财务指标
- `init_balance`: 初始资金
- `final_balance`: 最终资金
- `total_return`: 总收益率（小数形式，0.3734 表示 37.34%）
- `annual_return`: 年化收益率
- `total_commission`: 总手续费

#### 风险指标
- `sharpe_ratio`: 夏普比率（使用 backtrader 内置分析器计算）
- `max_drawdown`: 最大回撤（小数形式，0.28 表示 28%）
- `calmar_ratio`: Calmar 比率（年化收益率/最大回撤）
- `vwr`: 变异加权收益率（Variability-Weighted Return）

#### 交易统计
- `trade_count`: 交易次数
- `winning_percentage`: 胜率（小数形式，0.4 表示 40%）
- `trades`: 每笔交易的详细信息数组
  - `time`: 交易时间
  - `balance`: 交易后账户余额
  - `price`: 交易价格
  - `size`: 交易数量（0.0 表示平仓）
  - `pnl`: 毛利润
  - `pnlcomm`: 净利润（扣除手续费）
  - `commission`: 手续费

## 策略开发

### 策略文件结构

每个策略文件必须包含一个名为 `Strategy` 的类，继承自 `backtrader.Strategy`：

```python
import backtrader as bt

class Strategy(bt.Strategy):
    """策略类"""
    
    params = (
        ('param1', 10),    # 策略参数
        ('param2', 0.95),
    )
    
    def __init__(self):
        """初始化策略"""
        # 计算技术指标
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0].close, 
            period=self.params.param1
        )
    
    def next(self):
        """策略主逻辑"""
        # 交易逻辑
        if not self.position:
            if self.sma[0] > self.sma[-1]:  # 上升趋势
                self.buy()
        else:
            if self.sma[0] < self.sma[-1]:  # 下降趋势
                self.sell()
```

### 内置策略

#### 1. simple_ma.py - 简单移动平均策略

- 使用短期和长期移动平均线
- 金叉买入，死叉卖出
- 参数：short_period (10), long_period (30), position_size (0.95)

#### 2. rsi_ma.py - RSI + 移动平均策略

- 结合 RSI 指标和移动平均线
- RSI 超卖且价格在均线上方时买入
- RSI 超买或价格跌破均线时卖出
- 包含止损和止盈机制
- 参数：rsi_period (14), ma_period (20), stop_loss (0.05), take_profit (0.15)

## 核心技术特性

### 动态时间框架配置

系统会根据输入的时间间隔自动配置所有分析器的 `timeframe` 和 `compression` 参数：

| 时间间隔 | timeframe | compression | 说明 |
|---------|-----------|-------------|------|
| 1m | Minutes | 1 | 1 分钟 |
| 15m | Minutes | 15 | 15 分钟 |
| 1h | Minutes | 60 | 1 小时 = 60 分钟 |
| 4h | Minutes | 240 | 4 小时 = 240 分钟 |
| 1d | Days | 1 | 1 天 |

### 内置分析器使用

系统优先使用 backtrader 内置分析器确保计算准确性：

#### 需要时间框架参数的分析器
- **SharpeRatio**: 夏普比率计算
- **Returns**: 收益率分析
- **Calmar**: Calmar 比率计算
- **VWR**: 变异加权收益率

#### 无需额外参数的分析器
- **DrawDown**: 最大回撤分析
- **TradeAnalyzer**: 交易统计分析
- **AnnualReturn**: 年化收益率计算

### 指标计算原理

#### 夏普比率
- 使用 backtrader 内置 SharpeRatio 分析器
- 根据数据时间间隔自动设置年化参数
- 无风险利率默认为 0%
- 公式：(年化收益率 - 无风险利率) / 年化波动率

#### 最大回撤
- 使用 backtrader 内置 DrawDown 分析器
- 计算资金曲线从峰值到谷值的最大跌幅
- 返回小数形式（0.28 表示 28%）

#### Calmar 比率
- 年化收益率 / 最大回撤
- 衡量风险调整后的收益能力
- 值越高表示策略越优秀

## 安装和运行

### 依赖安装

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install backtrader pandas numpy pymysql PyYAML
```

### 运行示例

```bash
# 基本回测
python3 index.py --currency BTCUSDT --time_interval 4h --strategy_name simple_ma

# 不同时间间隔
python3 index.py --currency ETHUSDT --time_interval 1h --strategy_name rsi_ma

# 日线数据
python3 index.py --currency BTCUSDT --time_interval 1d --strategy_name buy_hold
```

## 系统架构

### 核心组件

1. **BacktestEngine**: 主回测引擎
   - 数据加载和预处理
   - 策略动态加载
   - 分析器配置管理
   - 回测执行控制

2. **时间间隔解析器**: `_parse_time_interval()`
   - 智能解析时间间隔字符串
   - 自动映射到 backtrader 时间框架
   - 支持多种时间单位

3. **内置分析器集成**:
   - 自动配置分析器参数
   - 统一的指标提取接口
   - 完整的错误处理机制

### 数据流程

```
MySQL K线数据 → 数据加载 → Pandas DataFrame → backtrader Feed → 策略执行 → 分析器计算 → JSON结果输出
```

## 最佳实践

### 数据准备
1. **确保数据质量**：MySQL 数据库中有足够的历史 K 线数据
2. **时间一致性**：确保数据库时间和系统时间一致
3. **数据完整性**：避免数据缺失或异常值

### 策略开发
1. **标准结构**：策略文件必须包含 `Strategy` 类
2. **参数化设计**：使用 `params` 定义可调参数
3. **日志记录**：在关键位置添加日志输出
4. **风险控制**：实现止损和仓位管理

### 性能优化
1. **向量化计算**：优先使用 pandas/numpy 向量化操作
2. **内存管理**：大数据量时注意内存使用
3. **数据库优化**：使用索引优化查询性能

## 技术优势

### 计算准确性
- ✅ 使用 backtrader 官方内置分析器
- ✅ 动态时间框架配置确保指标准确
- ✅ 完整的单元测试覆盖

### 系统稳定性
- ✅ 完善的错误处理和异常捕获
- ✅ 输入参数验证和边界检查
- ✅ 数据库连接池管理

### 扩展能力
- ✅ 模块化设计，易于添加新功能
- ✅ 支持自定义策略和分析器
- ✅ 灵活的配置系统

## 常见问题

### Q: 如何添加新策略？
A: 在 strategy 文件夹下创建新的 .py 文件，包含 Strategy 类即可。系统会自动加载。

### Q: 支持哪些技术指标？
A: 支持 backtrader 的所有内置指标（MA、RSI、MACD、布林带等），也可以自定义指标。

### Q: 如何调整手续费？
A: 修改 BacktestEngine 类中的 commission 参数，默认为 0.001（0.1%）。

### Q: 数据不足怎么办？
A: 系统会提示数据不足，请确保数据库中有足够的历史数据。建议至少有 100 个数据点。

### Q: 为什么夏普比率和其他系统不一样？
A: 本系统使用 backtrader 内置分析器，并根据数据时间间隔动态设置参数，确保计算准确性。

### Q: 如何查看详细的分析器配置？
A: 参考 `ANALYZER_CONFIGURATION.md` 文档了解所有分析器的详细配置说明。

### Q: 支持哪些时间间隔？
A: 支持从 1 分钟到 1 月的所有常见时间间隔，系统会自动解析并配置相应的分析器参数。

---

## 更多文档

- [分析器配置说明](ANALYZER_CONFIGURATION.md)
- [Python 依赖包列表](requirements.txt)

## 版本历史

- **v2.0**: 重构分析器系统，使用 backtrader 内置分析器
- **v1.5**: 添加动态时间框架配置
- **v1.0**: 基础回测功能实现
