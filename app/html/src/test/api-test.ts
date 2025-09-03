// API 测试文件
// 用于测试新的 getData 接口

import api, { getData } from '../services/api';

// 测试用例
export const testGetData = async () => {
  console.log('🧪 开始测试 getData 接口...\n');

  try {
    // 测试1: 基本的 getStrategy 调用
    console.log('📋 测试1: 基本 getStrategy 调用');
    const result1 = await getData('getStrategy', {
      page: 1,
      pageSize: 5
    });
    console.log('✅ 成功:', result1.success);
    console.log('📊 策略数量:', result1.data?.strategies?.length || 0);
    console.log('📈 总记录数:', result1.data?.pagination?.total || 0);

    // 测试2: 带排序的 getStrategy 调用
    console.log('\n📋 测试2: 带排序的 getStrategy 调用');
    const result2 = await getData('getStrategy', {
      page: 1,
      pageSize: 3,
      orderBy: 'sharpe_ratio',
      order: 'desc'
    });
    console.log('✅ 成功:', result2.success);
    if (result2.data?.strategies?.length > 0) {
      const topStrategy = result2.data.strategies[0];
      console.log('🏆 最高夏普比率策略:', topStrategy.name);
      console.log('📊 夏普比率:', topStrategy.sharpe_ratio);
    }

    // 测试3: 错误处理
    console.log('\n📋 测试3: 错误处理');
    const result3 = await getData('invalidMethod', {});
    console.log('❌ 预期失败:', !result3.success);
    console.log('💬 错误信息:', result3.message);

    // 测试4: 使用原有的 strategyApi（向后兼容性测试）
    console.log('\n📋 测试4: 向后兼容性测试');
    const result4 = await api.strategy.getStrategies({
      page: 1,
      pageSize: 2,
      orderBy: 'findal_balance',
      order: 'desc'
    });
    console.log('✅ 向后兼容成功:', result4.success);

    console.log('\n🎉 所有 getData 测试完成！');
    return true;

  } catch (error) {
    console.error('❌ 测试失败:', error);
    return false;
  }
};

// 使用示例
export const apiUsageExamples = {
  // 方式1: 使用新的 getData 接口
  async getStrategyList() {
    return await getData('getStrategy', {
      page: 1,
      pageSize: 10,
      orderBy: 'sharpe_ratio',
      order: 'desc'
    });
  },

  // 方式2: 使用默认导出的 getData
  async getStrategyListAlt() {
    return await api.getData('getStrategy', {
      page: 1,
      pageSize: 20
    });
  },

  // 方式3: 使用专门的 strategyApi（向后兼容）
  async getStrategyListCompat() {
    return await api.strategy.getStrategies({
      page: 1,
      pageSize: 15,
      orderBy: 'trade_count',
      order: 'asc'
    });
  }
};

// 如果在浏览器环境中运行，添加到全局对象
if (typeof window !== 'undefined') {
  (window as any).testGetData = testGetData;
  (window as any).apiUsageExamples = apiUsageExamples;
  console.log('💡 可以在浏览器控制台中运行: testGetData()');
}
