# Backtrader 分析器配置说明

## 概述

本文档说明了回测系统中所有使用的 backtrader 内置分析器的配置情况，特别是 `timeframe` 和 `compression` 参数的设置。

## 分析器分类

### 需要 timeframe 和 compression 参数的分析器

这些分析器需要根据数据的时间间隔动态设置 `timeframe` 和 `compression` 参数：

#### 1. SharpeRatio（夏普比率）
- **参数**: `timeframe`, `compression`, `riskfreerate=0.0`
- **用途**: 计算风险调整后的收益率
- **设置**: 根据数据间隔动态设置

#### 2. Returns（收益率）
- **参数**: `timeframe`, `compression`
- **用途**: 计算指定时间框架内的收益率
- **设置**: 根据数据间隔动态设置

#### 3. Calmar（Calmar 比率）
- **参数**: `timeframe`, `compression`
- **用途**: 计算年化收益率与最大回撤的比率
- **设置**: 根据数据间隔动态设置

#### 4. VWR（变异加权收益率）
- **参数**: `timeframe`, `compression`
- **用途**: 计算考虑波动性的加权收益率
- **设置**: 根据数据间隔动态设置

### 不需要额外参数的分析器

这些分析器使用默认参数即可正常工作：

#### 1. DrawDown（回撤分析）
- **参数**: 无特殊参数
- **用途**: 计算最大回撤、回撤持续时间等
- **设置**: 直接添加即可

#### 2. TradeAnalyzer（交易分析）
- **参数**: 无特殊参数
- **用途**: 分析交易统计信息（胜率、交易次数等）
- **设置**: 直接添加即可

#### 3. AnnualReturn（年化收益率）
- **参数**: 无特殊参数
- **用途**: 计算年化收益率
- **设置**: 直接添加即可

## 时间间隔映射规则

系统会根据输入的时间间隔字符串自动解析为对应的 `timeframe` 和 `compression`：

| 时间间隔 | timeframe | compression | 说明 |
|---------|-----------|-------------|------|
| 1m | Minutes | 1 | 1分钟 |
| 5m | Minutes | 5 | 5分钟 |
| 15m | Minutes | 15 | 15分钟 |
| 1h | Minutes | 60 | 1小时 = 60分钟 |
| 4h | Minutes | 240 | 4小时 = 240分钟 |
| 12h | Minutes | 720 | 12小时 = 720分钟 |
| 1d | Days | 1 | 1天 |
| 1w | Weeks | 1 | 1周 |
| 1M | Months | 1 | 1月（注意大写M） |

## 代码实现

```python
# 解析时间间隔
timeframe, compression = self._parse_time_interval(self.time_interval)

# 需要 timeframe 和 compression 参数的分析器
self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', 
                        timeframe=timeframe, compression=compression, riskfreerate=0.0)
self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns',
                        timeframe=timeframe, compression=compression)
self.cerebro.addanalyzer(bt.analyzers.Calmar, _name='calmar',
                        timeframe=timeframe, compression=compression)
self.cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr',
                        timeframe=timeframe, compression=compression)

# 不需要额外参数的分析器
self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
self.cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annual_return')
```

## 优势

1. **计算准确性**: 所有分析器都使用与数据间隔一致的时间框架
2. **动态适配**: 支持从1分钟到1月的各种数据间隔
3. **规范遵循**: 完全符合 backtrader 的最佳实践
4. **易于维护**: 统一的参数设置逻辑

## 验证

系统在启动时会显示解析结果：
```
📊 时间间隔 '4h' 解析为：Minutes, compression=240
```

这确保了所有支持的分析器都使用正确的时间框架参数。
