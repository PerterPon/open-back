import React from 'react';
import { Card, Row, Col, Statistic, Typography, Space } from 'antd';
import {
  DollarOutlined,
  TrophyOutlined,
  LineChartOutlined,
  TeamOutlined,
} from '@ant-design/icons';

const { Title, Paragraph } = Typography;

const Home: React.FC = () => {
  return (
    <div>
      {/* 页面标题 */}
      <Typography style={{ marginBottom: 24 }}>
        <Title level={2}>
          欢迎来到 OpenBack 策略管理系统 🚀
        </Title>
        <Paragraph type="secondary">
          这是一个专业的量化交易策略管理平台，帮助您分析和管理交易策略。
        </Paragraph>
      </Typography>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总策略数"
              value={6880}
              prefix={<TrophyOutlined style={{ color: '#1890ff' }} />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="平均夏普比率"
              value={0.0197}
              precision={4}
              prefix={<LineChartOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="平均胜率"
              value={56.21}
              suffix="%"
              prefix={<DollarOutlined style={{ color: '#faad14' }} />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="活跃用户"
              value={12}
              prefix={<TeamOutlined style={{ color: '#f5222d' }} />}
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 功能介绍卡片 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} md={12}>
          <Card 
            title="🎯 核心功能" 
            style={{ height: '100%' }}
            headStyle={{ backgroundColor: '#fafafa' }}
          >
            <Space direction="vertical" size="middle">
              <div>
                <strong>策略管理</strong>
                <br />
                <span style={{ color: '#666' }}>
                  查看、分析和管理您的量化交易策略，支持多维度排序和筛选。
                </span>
              </div>
              <div>
                <strong>性能分析</strong>
                <br />
                <span style={{ color: '#666' }}>
                  深入分析策略的夏普比率、最大回撤、胜率等关键指标。
                </span>
              </div>
              <div>
                <strong>实时监控</strong>
                <br />
                <span style={{ color: '#666' }}>
                  实时监控策略运行状态，及时发现问题和机会。
                </span>
              </div>
            </Space>
          </Card>
        </Col>
        
        <Col xs={24} md={12}>
          <Card 
            title="📊 数据概览" 
            style={{ height: '100%' }}
            headStyle={{ backgroundColor: '#fafafa' }}
          >
            <Space direction="vertical" size="middle">
              <div>
                <strong>Hello World! 🌍</strong>
                <br />
                <span style={{ color: '#666' }}>
                  欢迎使用OpenBack策略管理系统！这是您的控制中心。
                </span>
              </div>
              <div>
                <strong>数据实时同步</strong>
                <br />
                <span style={{ color: '#666' }}>
                  系统已连接到数据库，当前共有 <strong>6,880</strong> 条策略记录。
                </span>
              </div>
              <div>
                <strong>快速开始</strong>
                <br />
                <span style={{ color: '#666' }}>
                  点击左侧"策略管理"菜单开始探索您的交易策略数据。
                </span>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Home;
