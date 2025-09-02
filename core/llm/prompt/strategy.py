"""
LLM 提示词：用于生成交易策略
"""

generate_strategy = """你是一个世界上最最顶级的比特币量化交易员，你可以写出夏普比率大于 2 的策略，现在我正在回测比特币从 2024 年开始的一小时的数据的 K 线，回测框架是 Python 的 backTrader，我已经搭建了整体工程框架了，你帮我完成一下这个 LLMStrategy 类吧，并请遵循如下要求：

# Strategy 开头
import backtrader as bt

class LLMStrategy(bt.Strategy):
  def __init__(self):
    print("LLMStrategy init")

  def next(self):
    print("LLMStrategy next")

# 要求
0. 注意：我的策略是基于著名 python 回测框架 backTrader 写的，写之前请务必先仔细阅读和留意 backTrader 的语法和用法，不要犯低级错误。
1. [重要！重要！重要！] 请直接返回给我策略代码，不要添加任何内容。不要添加除了代码之外的任何说明性内容，示例如下：
  1.1 注意，不用实现 notify_trade 方法，也就是策略运行时不要添加任何 print 输出。
  1.2 手续费和滑点我已经设置好了，这个你不用考虑。

## 示例
import backtrader as bt

class LLMStrategy(bt.Strategy):
  def __init__(self):
    print("LLMStrategy init")

  def next(self):
    print("LLMStrategy next")

2. 请发挥你的聪明才智，可以使用各类量化策略，我们的目标只有一个，就是追求足够高的收益、夏普比率以及更低的回撤。
3. 我会给你到目前为止，效果最好的一个策略，你可以参考这个策略，继续进行优化，或者如果你觉得已经没有优化空间了，那么也可以换一个思路，重新写一个策略，记住，一切的目标就是追求更高的收益。
4. 策略需要保持适当的交易次数，不要过于频繁，也不要过于稀疏，按照咱们得数据来看，交易次数可以保持在 100 次左右。
5. 不要输出 markdown 格式，纯文本就可以，比如不要加上\`\`\`python 和\`\`\`。
6. 代码中不要加任何的 print。

# backTrader 语法注意事项
1. 在 backtrader 中，指标对象不支持 Python 的切片操作
  atr[-30:].mean()  # ❌ 错误：不能对指标使用切片
  解决方案：使用 backtrader 的内置指标来计算均值：
  正确：使用 SMA 指标计算 30 期均值
  atr_ma = bt.indicators.SMA(atr, period=30)

# 重要！重要！重要！
直接返回给我代码，不要用 markdown 返回给我，我会直接把你给我的返回结果当做代码运行，所以不要加任何说明性文字。
"""


