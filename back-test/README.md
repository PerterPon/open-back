# 回测系统使用说明

## 概述

这是一个基于 backtrader 框架的加密货币交易策略回测系统。系统从 MySQL 数据库读取 K 线数据，动态加载策略文件，执行回测并计算各种性能指标。

## 文件结构

```
back-test/
├── index.py              # 主回测文件
├── test_backtest.py      # 测试文件
├── README.md            # 使用说明
└── strategy/            # 策略文件夹
    ├── simple_ma.py     # 简单移动平均策略
    └── rsi_ma.py        # RSI + 移动平均策略
```

## 使用方法

### 基本用法

```bash
python index.py --currency BTCUSDT --time_interval 1h --strategy_name simple_ma
```

### 参数说明

- `--currency`: 货币对，如 BTCUSDT、ETHUSDT 等
- `--time_interval`: 时间间隔，如 1m、5m、1h、1d 等
- `--strategy_name`: 策略名称，对应 strategy 文件夹下的 Python 文件名

### 输出格式

系统会输出 JSON 格式的回测结果：

```json
{
  "currency": "BTCUSDT",
  "time_interval": "1h",
  "sharpe_ratio": "1.5",
  "trade_count": 25,
  "trades": [
    {
      "time": "2023-06-15 22:00:00",
      "balance": 10025.76,
      "price": 25389.97,
      "size": 0.4,
      "pnl": 25.76,
      "pnlcomm": 23.26,
      "commission": 2.5
    }
  ],
  "total_commission": 125.50,
  "max_drawdown": 0.0523,
  "winning_percentage": 0.64,
  "init_balance": 10000.0,
  "final_balance": 10523.45,
  "total_return": 0.0523,
  "data_points": 1000,
  "start_date": "2023-01-01 00:00:00",
  "end_date": "2023-06-30 23:00:00"
}
```

### 字段说明

- `currency`: 货币对
- `time_interval`: 时间间隔
- `sharpe_ratio`: 夏普比率（字符串格式）
- `trade_count`: 交易次数
- `trades`: 每笔交易的详细信息数组
- `total_commission`: 总手续费
- `max_drawdown`: 最大回撤（小数形式，0.05 表示 5%）
- `winning_percentage`: 胜率（小数形式）
- `init_balance`: 初始资金
- `final_balance`: 最终资金
- `total_return`: 总收益率
- `data_points`: 数据点数量
- `start_date`: 回测开始日期
- `end_date`: 回测结束日期

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

## 指标计算说明

### 夏普比率

系统会根据数据的实际时间跨度自动计算年化夏普比率：

- 1m 数据：每年 365×24×60 个数据点
- 5m 数据：每年 365×24×12 个数据点
- 1h 数据：每年 365×24 个数据点
- 1d 数据：每年 365 个数据点

公式：夏普比率 = (年化收益率 - 无风险收益率) / 年化波动率

### 最大回撤

计算资金曲线从峰值到谷值的最大跌幅，用小数表示（如 0.05 表示 5%）。

### 胜率

盈利交易次数 / 总交易次数，用小数表示。

## 测试

运行测试文件验证系统功能：

```bash
python test_backtest.py
```

测试包括：
- 数据加载功能测试
- 策略加载功能测试
- 指标计算准确性测试
- 完整回测流程测试
- 边界条件测试

## 依赖要求

```bash
pip install backtrader pandas numpy pymysql
```

## 注意事项

1. **数据质量**：确保 MySQL 数据库中有足够的 K 线数据
2. **策略文件**：策略文件必须包含 `Strategy` 类
3. **内存使用**：大量数据可能消耗较多内存
4. **计算精度**：所有指标都经过精确计算和验证
5. **时区问题**：确保数据库时间和系统时间一致

## 错误处理

系统包含完善的错误处理机制：
- 数据加载失败会返回错误信息
- 策略文件不存在会提示错误
- 计算过程中的异常会被捕获并记录

## 扩展性

系统设计具有良好的扩展性：
- 可以轻松添加新的技术指标
- 支持自定义分析器
- 可以扩展输出格式
- 支持多种数据源

## 性能优化

- 使用向量化计算提高效率
- 优化数据库查询
- 合理的内存管理
- 并行处理支持（可扩展）

## 常见问题

### Q: 如何添加新策略？
A: 在 strategy 文件夹下创建新的 .py 文件，包含 Strategy 类即可。

### Q: 支持哪些技术指标？
A: 支持 backtrader 的所有内置指标，也可以自定义指标。

### Q: 如何调整手续费？
A: 修改 BacktestEngine 类中的 commission 参数。

### Q: 数据不足怎么办？
A: 系统会提示数据不足，请确保数据库中有足够的历史数据。
