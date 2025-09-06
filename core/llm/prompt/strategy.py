"""
LLM 提示词：用于生成交易策略
"""

generate_strategy = """你是一个世界顶级的加密货币量化交易专家，具备深厚的金融工程背景和丰富的实战经验。现在需要你为数字货币的 K 线数据（2024 年开始）设计一个高性能的量化交易策略，使用 Python backTrader 框架实现，最后我会给你目前最高收益的策略，请先分析这个策略为什么是最厉害的，然后可以基于这个策略进行优化。

# 策略目标与约束
## 核心目标
- 夏普比率 > 2.0
- 最大回撤 < 15%
- 年化收益率 > 30%
- 交易次数控制在 200-320 次之间（避免过度交易和交易稀疏）

## 风险管理要求（必须实现）
- 必须包含止损机制（建议 ATR 动态止损或固定百分比止损）
- 仓位管理：单次交易风险不超过总资金的 10%
- 连续亏损保护：连续 3 次亏损后降低仓位或暂停交易

# 策略设计指导
## 推荐策略类型（选择其一或组合）
1. **趋势跟踪策略**：双均线突破、MACD 金叉死叉、布林带突破
2. **均值回归策略**：RSI 超买超卖、布林带回归、价格偏离均线
3. **动量策略**：价格突破、成交量确认、相对强弱指数
4. **多因子策略**：技术指标组合、市场微观结构分析

## 技术指标建议
- **趋势指标**：SMA、EMA、MACD、ADX、Parabolic SAR
- **震荡指标**：RSI、Stochastic、Williams %R、CCI
- **波动率指标**：ATR、Bollinger Bands、Keltner Channels
- **成交量指标**：OBV、VWAP、Volume Rate of Change

## 加密货币市场特性考虑
- 24/7交易，注意周末和节假日的流动性变化
- 高波动性，需要更宽的止损空间
- 情绪驱动明显，考虑技术面与基本面结合
- 关注重要支撑阻力位和心理价位

# 代码实现要求
## 格式要求
- 直接返回 Python 代码，不要 markdown 格式
- 不要添加任何说明文字或注释
- 不要使用 print 语句
- 不需要实现 notify_trade 方法

## 代码结构
import backtrader as bt

class LLMStrategy(bt.Strategy):
    def __init__(self):
        # 初始化技术指标和参数
        pass
    
    def next(self):
        # 实现交易逻辑
        pass

## backTrader 语法要点
- 指标对象不支持切片：使用 bt.indicators.SMA(indicator, period=N) 而非 indicator[-N:].mean()
- 数据访问：self.data.close[0] 当前价格，self.data.close[-1] 前一根 K 线
- 订单管理：self.buy()、self.sell()、self.close()
- 仓位检查：self.position.size 判断当前仓位

# 策略优化建议
1. **参数优化**：使用经过统计验证的参数，避免过拟合
2. **多时间框架**：可以参考更高时间框架的趋势方向
3. **动态调整**：根据市场波动率动态调整止损和仓位
4. **回测稳健性**：确保策略在不同市场环境下都有良好表现

# 重要提醒
- 手续费和滑点已配置，无需考虑
- 专注于策略逻辑的有效性和风险控制
- 代码必须能直接运行，语法正确
- 追求风险调整后收益最大化，而非单纯高收益

# 目前最高收益策略代码
__current_highest_strategy__

# 最高收益的相关数据
__current_highest_strategy_sharpe_ratio__
__current_highest_strategy_max_drawdown__
__current_highest_strategy_trade_count__
__current_highest_strategy_winning_percentage__
__current_highest_strategy_total_commission__
__current_highest_strategy_final_balance__

直接返回策略代码，不要任何额外内容：
"""


