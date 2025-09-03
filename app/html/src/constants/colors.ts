// 颜色常量定义
export const COLORS = {
  // 成功/盈利颜色
  SUCCESS: '#52c41a',
  SUCCESS_BG: '#f6ffed',
  SUCCESS_BORDER: '#b7eb8f',
  
  // 失败/亏损颜色  
  ERROR: '#f5222d',
  ERROR_BG: '#fff2f0',
  ERROR_BORDER: '#ffccc7',
  
  // 中性颜色
  NEUTRAL: '#666666',
  NEUTRAL_BG: '#f5f5f5',
  
  // 警告颜色
  WARNING: '#faad14',
  WARNING_BG: '#fffbe6',
} as const;

// 主题相关颜色（支持亮色/暗色主题）
export const getThemeColors = (isDark: boolean = false) => ({
  success: isDark ? '#73d13d' : COLORS.SUCCESS,
  error: isDark ? '#ff7875' : COLORS.ERROR,
  neutral: isDark ? '#a6a6a6' : COLORS.NEUTRAL,
  warning: isDark ? '#ffd666' : COLORS.WARNING,
});

// 策略表格专用颜色判断函数
export const getStrategyFieldColor = (
  field: 'winning_percentage' | 'max_drawdown' | 'final_balance',
  value: number,
  compareValue?: number,
  isDark: boolean = false
) => {
  const colors = getThemeColors(isDark);
  
  switch (field) {
    case 'winning_percentage':
      // 胜率大于50%为绿色
      return (value * 100) > 50 ? colors.success : colors.error;
      
    case 'max_drawdown':
      // 最大回撤小于30%为绿色
      return value < 0.3 ? colors.success : colors.error;
      
    case 'final_balance':
      // 最终余额大于初始余额为绿色
      return compareValue !== undefined && value > compareValue 
        ? colors.success 
        : colors.error;
        
    default:
      return colors.neutral;
  }
};
