import React from 'react';
import { Card, Typography } from 'antd';

const { Title } = Typography;

const Settings: React.FC = () => {
  return (
    <div>
      <Title level={2}>系统设置</Title>
      <Card>
        <p>系统设置页面正在开发中...</p>
        <p>这里将包含系统配置、用户管理等功能。</p>
      </Card>
    </div>
  );
};

export default Settings;
