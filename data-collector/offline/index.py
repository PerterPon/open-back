# 这个文件的作用是获取离线数据，数据从 binance 获取，运行这个文件的时候可以传参数，参数为：
# currency, 比如 BTCUSDT
# interval，时间间隔，比如 1h, 1d
# startDate，默认获取两年的数据。
# 具体的获取逻辑如下：
# 1. 首先调用调用数据库，从 kline 表中获取当前 currency 和 interval 的历史数据，然后去 binance 获取最新的数据，然后插入到 kline 表中。比如我们现在要获取 2020-01-01 到 2023-01-01 的数据，数据表中已经有 2020-01-01 到 2022-01-01 的数据，那么我们只需要获取 2022-01-01 到 2023-01-01 的数据即可。
# 2. 获取 K 线数据的时候如果当前 interval 的数据没有 close，那么就不要插入到数据表中。

import sys
import os
import argparse
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.mysql.kline import (
    get_klines_by_currency_time_interval, 
    get_latest_by_currency_time_interval, 
    batch_create_klines
)


class BinanceKlineCollector:
    """Binance K线数据收集器"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com"
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('BinanceKlineCollector')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _convert_interval(self, interval: str) -> str:
        """
        转换时间间隔格式，确保与 Binance API 兼容
        Args:
            interval: 时间间隔，如 1h, 1d, 4h, 1m
        Returns:
            Binance API 兼容的时间间隔
        """
        # Binance 支持的时间间隔
        valid_intervals = [
            '1s', '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h',
            '1d', '3d', '1w', '1M'
        ]
        
        if interval in valid_intervals:
            return interval
        
        # 尝试一些常见的转换
        interval_map = {
            '1min': '1m',
            '5min': '5m',
            '15min': '15m',
            '30min': '30m',
            '1hour': '1h',
            '4hour': '4h',
            '1day': '1d',
            '1week': '1w',
            '1month': '1M'
        }
        
        return interval_map.get(interval, interval)
    
    def _timestamp_to_datetime(self, timestamp: int) -> datetime:
        """
        将时间戳转换为 datetime 对象
        Args:
            timestamp: 毫秒时间戳
        Returns:
            datetime 对象
        """
        return datetime.fromtimestamp(timestamp / 1000)
    
    def _datetime_to_timestamp(self, dt: datetime) -> int:
        """
        将 datetime 对象转换为毫秒时间戳
        Args:
            dt: datetime 对象
        Returns:
            毫秒时间戳
        """
        return int(dt.timestamp() * 1000)
    
    def get_klines_from_binance(self, symbol: str, interval: str, start_time: Optional[datetime] = None, 
                               end_time: Optional[datetime] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        从 Binance API 获取 K 线数据
        Args:
            symbol: 交易对符号，如 BTCUSDT
            interval: 时间间隔
            start_time: 开始时间
            end_time: 结束时间
            limit: 限制数量，最大 1000
        Returns:
            K 线数据列表
        """
        url = f"{self.base_url}/api/v3/klines"
        
        params = {
            'symbol': symbol.upper(),
            'interval': self._convert_interval(interval),
            'limit': min(limit, 1000)
        }
        
        if start_time:
            params['startTime'] = self._datetime_to_timestamp(start_time)
        
        if end_time:
            params['endTime'] = self._datetime_to_timestamp(end_time)
        
        try:
            self.logger.info(f"正在从 Binance 获取 {symbol} {interval} 的 K 线数据...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            raw_data = response.json()
            
            # 转换为标准格式
            klines = []
            for item in raw_data:
                # Binance K线数据格式：
                # [
                #   1499040000000,      // 开盘时间
                #   "0.01634790",       // 开盘价
                #   "0.80000000",       // 最高价
                #   "0.01575800",       // 最低价
                #   "0.01577100",       // 收盘价
                #   "148976.11427815",  // 成交量
                #   1499644799999,      // 收盘时间
                #   "2434.19055334",    // 成交额
                #   308,                // 成交笔数
                #   "1756.87402397",    // 主动买入成交量
                #   "28.46694368",      // 主动买入成交额
                #   "17928899.62484339" // 忽略此参数
                # ]
                
                open_time = self._timestamp_to_datetime(item[0])
                close_time = self._timestamp_to_datetime(item[6])
                
                # 检查是否有收盘价，如果没有则跳过
                if item[4] is None or item[4] == '0' or item[4] == '':
                    continue
                
                kline = {
                    'currency': symbol.upper(),
                    'time_interval': interval,
                    'time': open_time,
                    'o': float(item[1]) if item[1] else 0.0,  # 开盘价
                    'h': float(item[2]) if item[2] else 0.0,  # 最高价
                    'l': float(item[3]) if item[3] else 0.0,  # 最低价
                    'c': float(item[4]) if item[4] else 0.0,  # 收盘价
                    'v': float(item[5]) if item[5] else 0.0,  # 成交量
                    'extra': f'{{"close_time": "{close_time.isoformat()}", "trades": {item[8]}, "quote_volume": "{item[7]}"}}',
                    'comment': f'从 Binance 获取的 {interval} K 线数据'
                }
                
                klines.append(kline)
            
            self.logger.info(f"成功获取 {len(klines)} 条 K 线数据")
            return klines
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求 Binance API 失败：{e}")
            return []
        except Exception as e:
            self.logger.error(f"处理 Binance 数据时出错：{e}")
            return []
    
    def get_missing_data_range(self, currency: str, time_interval: str, 
                              start_date: datetime, end_date: datetime) -> List[tuple]:
        """
        获取缺失的数据时间范围
        Args:
            currency: 货币对
            time_interval: 时间间隔
            start_date: 开始日期
            end_date: 结束日期
        Returns:
            缺失数据的时间范围列表
        """
        # 使用 core/mysql/kline.py 中的函数获取数据库中现有的最新数据
        latest_record = get_latest_by_currency_time_interval(currency, time_interval)
        
        missing_ranges = []
        
        if latest_record is None:
            # 如果没有任何数据，则整个时间范围都需要获取
            missing_ranges.append((start_date, end_date))
            self.logger.info(f"数据库中没有 {currency} {time_interval} 的数据，需要获取 {start_date} 到 {end_date} 的数据")
        else:
            latest_time = latest_record['time']
            if isinstance(latest_time, str):
                latest_time = datetime.fromisoformat(latest_time.replace('Z', '+00:00'))
            
            self.logger.info(f"数据库中最新数据时间：{latest_time}")
            
            # 如果最新数据时间早于结束时间，则需要获取缺失的数据
            if latest_time < end_date:
                # 从最新数据的下一个时间点开始获取
                next_time = latest_time + timedelta(hours=1 if time_interval == '1h' else 1440 if time_interval == '1d' else 60)
                missing_ranges.append((next_time, end_date))
                self.logger.info(f"需要获取 {next_time} 到 {end_date} 的增量数据")
            else:
                self.logger.info("数据库中的数据已经是最新的，无需更新")
        
        return missing_ranges
    
    def collect_and_save_klines(self, currency: str, time_interval: str, 
                               start_date: datetime, end_date: datetime) -> int:
        """
        收集并保存 K 线数据
        Args:
            currency: 货币对
            time_interval: 时间间隔
            start_date: 开始日期
            end_date: 结束日期
        Returns:
            成功插入的记录数
        """
        total_inserted = 0
        
        # 获取缺失的数据时间范围
        missing_ranges = self.get_missing_data_range(currency, time_interval, start_date, end_date)
        
        for start_time, end_time in missing_ranges:
            current_time = start_time
            
            while current_time < end_time:
                # 计算本次请求的结束时间（最多获取 1000 条数据）
                if time_interval == '1h':
                    batch_end_time = min(current_time + timedelta(hours=1000), end_time)
                elif time_interval == '1d':
                    batch_end_time = min(current_time + timedelta(days=1000), end_time)
                elif time_interval == '4h':
                    batch_end_time = min(current_time + timedelta(hours=4000), end_time)
                elif time_interval == '1m':
                    batch_end_time = min(current_time + timedelta(minutes=1000), end_time)
                else:
                    batch_end_time = min(current_time + timedelta(hours=1000), end_time)
                
                # 从 Binance 获取数据
                klines = self.get_klines_from_binance(
                    symbol=currency,
                    interval=time_interval,
                    start_time=current_time,
                    end_time=batch_end_time,
                    limit=1000
                )
                
                if klines:
                    try:
                        # 使用 core/mysql/kline.py 中的函数批量插入数据库
                        inserted_count = batch_create_klines(klines)
                        total_inserted += inserted_count
                        self.logger.info(f"成功插入 {inserted_count} 条 K 线数据")
                        
                        # 更新当前时间为最后一条数据的时间
                        if klines:
                            last_kline_time = klines[-1]['time']
                            if isinstance(last_kline_time, str):
                                last_kline_time = datetime.fromisoformat(last_kline_time)
                            current_time = last_kline_time + timedelta(seconds=1)
                        else:
                            current_time = batch_end_time
                            
                    except Exception as e:
                        self.logger.error(f"插入数据库失败：{e}")
                        break
                else:
                    self.logger.warning("未获取到数据，跳过")
                    current_time = batch_end_time
                
                # 避免请求过于频繁
                time.sleep(0.1)
        
        return total_inserted


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='从 Binance 获取离线 K 线数据')
    
    parser.add_argument('--currency', '-c', type=str, required=True,
                       help='货币对，如 BTCUSDT')
    
    parser.add_argument('--interval', '-i', type=str, default='1h',
                       help='时间间隔，如 1h, 4h, 1d (默认：1h)')
    
    parser.add_argument('--start-date', '-s', type=str,
                       help='开始日期，格式：YYYY-MM-DD (默认：2年前)')
    
    parser.add_argument('--end-date', '-e', type=str,
                       help='结束日期，格式：YYYY-MM-DD (默认：今天)')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='显示详细日志')
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 解析日期参数
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        except ValueError:
            print("错误：开始日期格式不正确，请使用 YYYY-MM-DD 格式")
            return 1
    else:
        # 默认获取两年的数据
        start_date = datetime.now() - timedelta(days=730)
    
    if args.end_date:
        try:
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
        except ValueError:
            print("错误：结束日期格式不正确，请使用 YYYY-MM-DD 格式")
            return 1
    else:
        # 默认到今天
        end_date = datetime.now()
    
    # 验证日期范围
    if start_date >= end_date:
        print("错误：开始日期必须早于结束日期")
        return 1
    
    print(f"📊 开始收集 K 线数据")
    print(f"货币对：{args.currency}")
    print(f"时间间隔：{args.interval}")
    print(f"时间范围：{start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
    print("=" * 50)
    
    try:
        # 创建收集器并开始收集数据
        collector = BinanceKlineCollector()
        total_inserted = collector.collect_and_save_klines(
            currency=args.currency.upper(),
            time_interval=args.interval,
            start_date=start_date,
            end_date=end_date
        )
        
        print("=" * 50)
        print(f"✅ 数据收集完成！")
        print(f"总共插入 {total_inserted} 条 K 线数据")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        return 1
    except Exception as e:
        print(f"❌ 数据收集失败：{e}")
        return 1


if __name__ == "__main__":
    exit(main())