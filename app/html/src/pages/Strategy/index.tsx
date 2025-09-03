import React, { useState, useEffect } from 'react';
import { Card, Typography, Table, message, Spin, theme } from 'antd';
import type { ColumnsType, TableProps } from 'antd/es/table';
import { getData } from '../../services/api';
import { getStrategyFieldColor } from '../../constants/colors';

const { Title } = Typography;

// 策略数据接口定义
interface StrategyData {
  id: number;
  name: string;
  currency: string;
  time_interval: string;
  sharpe_ratio: number;
  findal_balance: number;
  max_drawdown: number;
  trade_count: number;
  total_commission: number;
  winning_percetage: number;
  init_balance: number;
  created_at: string;
  updated_at: string;
}

// 分页信息接口
interface PaginationInfo {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// API 响应接口
interface StrategyResponse {
  strategies: StrategyData[];
  pagination: PaginationInfo;
  sorting: {
    orderBy: string | null;
    order: string;
  };
}

const Strategy: React.FC = () => {
  const [strategies, setStrategies] = useState<StrategyData[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [pagination, setPagination] = useState<PaginationInfo>({
    page: 1,
    pageSize: 50,
    total: 0,
    totalPages: 0,
    hasNext: false,
    hasPrev: false
  });

  // 获取当前主题信息
  const { token } = theme.useToken();
  const isDarkTheme = token.colorBgContainer === '#141414';

  // 表格列定义
  const columns: ColumnsType<StrategyData> = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      ellipsis: true,
    },
    {
      title: 'Currency',
      dataIndex: 'currency',
      key: 'currency',
      width: 120,
    },
    {
      title: 'Time Interval',
      dataIndex: 'time_interval',
      key: 'time_interval',
      width: 120,
    },
    {
      title: 'Sharpe Ratio',
      dataIndex: 'sharpe_ratio',
      key: 'sharpe_ratio',
      width: 120,
      sorter: true,
      render: (value: number) => value?.toFixed(6) || '-',
    },
    {
      title: 'Final Balance',
      dataIndex: 'findal_balance',
      key: 'findal_balance',
      width: 130,
      sorter: true,
      render: (value: number, record: StrategyData) => {
        if (value === undefined || value === null) return '-';
        const color = getStrategyFieldColor('final_balance', value, record.init_balance, isDarkTheme);
        return (
          <span style={{ 
            color,
            fontWeight: 'bold'
          }}>
            {value.toFixed(2)}
          </span>
        );
      },
    },
    {
      title: 'Max Drawdown',
      dataIndex: 'max_drawdown',
      key: 'max_drawdown',
      width: 130,
      sorter: true,
      render: (value: number) => {
        if (value === undefined || value === null) return '-';
        const color = getStrategyFieldColor('max_drawdown', value, undefined, isDarkTheme);
        return (
          <span style={{ 
            color,
            fontWeight: 'bold'
          }}>
            {value.toFixed(6)}
          </span>
        );
      },
    },
    {
      title: 'Trade Count',
      dataIndex: 'trade_count',
      key: 'trade_count',
      width: 110,
      sorter: true,
    },
    {
      title: 'Total Commission',
      dataIndex: 'total_commission',
      key: 'total_commission',
      width: 140,
      sorter: true,
      render: (value: number) => value?.toFixed(2) || '-',
    },
    {
      title: 'Winning Percentage',
      dataIndex: 'winning_percetage',
      key: 'winning_percetage',
      width: 150,
      render: (value: number) => {
        if (value === undefined || value === null) return '-';
        const color = getStrategyFieldColor('winning_percentage', value, undefined, isDarkTheme);
        return (
          <span style={{ 
            color,
            fontWeight: 'bold'
          }}>
            {(value * 100).toFixed(2)}%
          </span>
        );
      },
    },
    {
      title: 'Init Balance',
      dataIndex: 'init_balance',
      key: 'init_balance',
      width: 120,
      render: (value: number) => value?.toFixed(2) || '-',
    }
  ];

  // 获取策略数据
  const fetchStrategies = async (params: {
    page?: number;
    pageSize?: number;
    orderBy?: string;
    order?: 'asc' | 'desc';
  } = {}) => {
    setLoading(true);
    try {
      const response = await getData<StrategyResponse>('getStrategy', {
        page: params.page || pagination.page,
        pageSize: params.pageSize || pagination.pageSize,
        orderBy: params.orderBy,
        order: params.order || 'asc'
      });

      if (response.success) {
        setStrategies(response.data.strategies);
        setPagination(response.data.pagination);
        console.log('✅ 成功获取策略数据：', response.data.strategies.length, '条记录');
      } else {
        message.error(`获取策略数据失败：${response.message}`);
        console.error('❌ API 错误：', response.message);
      }
    } catch (error) {
      message.error('网络请求失败，请检查服务器连接');
      console.error('❌ 网络错误：', error);
    } finally {
      setLoading(false);
    }
  };

  // 页面加载时获取数据
  useEffect(() => {
    fetchStrategies({
      page: 1,
      pageSize: 50
    });
  }, []);

  // 处理表格变化（分页、排序）
  const handleTableChange: TableProps<StrategyData>['onChange'] = (paginationConfig, filters, sorter) => {
    const currentPage = paginationConfig?.current || 1;
    const currentPageSize = paginationConfig?.pageSize || 50;
    
    let orderBy: string | undefined;
    let order: 'asc' | 'desc' = 'asc';

    // 处理排序
    if (sorter && !Array.isArray(sorter)) {
      const field = sorter.field as string;
      // 支持排序的字段映射
      const sortableFields = ['sharpe_ratio', 'findal_balance', 'max_drawdown', 'trade_count', 'total_commission'];
      
      if (sortableFields.includes(field)) {
        orderBy = field;
        order = sorter.order === 'descend' ? 'desc' : 'asc';
      }
    }

    console.log('🔄 表格变化：', { page: currentPage, pageSize: currentPageSize, orderBy, order });

    fetchStrategies({
      page: currentPage,
      pageSize: currentPageSize,
      orderBy,
      order
    });
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={2}>策略管理</Title>
        <p style={{ marginBottom: '16px', color: '#666' }}>
          共 {pagination.total} 条策略记录，当前第 {pagination.page} 页，共 {pagination.totalPages} 页
        </p>
        
        <Spin spinning={loading}>
          <Table<StrategyData>
            columns={columns}
            dataSource={strategies}
            rowKey="id"
            pagination={{
              current: pagination.page,
              pageSize: pagination.pageSize,
              total: pagination.total,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) => 
                `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
              pageSizeOptions: ['20', '50', '100', '200'],
            }}
            onChange={handleTableChange}
            scroll={{ x: 1500 }}
            size="small"
            bordered
          />
        </Spin>
      </Card>
    </div>
  );
};

export default Strategy;
