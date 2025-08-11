# 这个文件是一个会被周期性运行的文件，先申明两个数组，第一个数组存储的是 currency，比如 BTCUSDT，第二个数组是 interval，比如 1m, 1h 等，这个程序会交叉遍历这两个数组，然后调用 offline/index.py 文件，获取离线数据，然后保存到 mysql 数据库中。

import sys
import os
import subprocess
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import concurrent.futures
import argparse

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class OfflineDataScheduler:
    """离线数据定时获取调度器"""
    
    def __init__(self):
        # 配置要获取数据的货币对列表
        self.currencies = [
            'BTCUSDT',
            'ETHUSDT', 
            'BNBUSDT',
            'ADAUSDT',
            'XRPUSDT',
            'SOLUSDT',
            'DOTUSDT',
            'DOGEUSDT',
            'AVAXUSDT',
            'LINKUSDT'
        ]
        
        # 配置要获取数据的时间间隔列表
        self.intervals = [
            '5m',
            '15m',
            '30m',
            '1h',
            '4h',
            '1d'
        ]
        
        # 默认获取最近 7 天的数据
        self.default_days = 720
        
        # 设置日志
        self.logger = self._setup_logger()
        
        # 获取 offline/index.py 的路径
        self.offline_script_path = os.path.join(os.path.dirname(__file__), 'offline', 'index.py')
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('OfflineDataScheduler')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # 控制台输出
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # 文件输出
            log_dir = os.path.join(os.path.dirname(__file__), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, f'offline_data_{datetime.now().strftime("%Y%m%d")}.log')
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def run_offline_collector(self, currency: str, interval: str, 
                             start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        运行离线数据收集器
        Args:
            currency: 货币对
            interval: 时间间隔
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        Returns:
            执行结果字典
        """
        try:
            # 构建命令参数
            cmd = [
                'python3', 
                self.offline_script_path,
                '--currency', currency,
                '--interval', interval
            ]
            
            if start_date:
                cmd.extend(['--start-date', start_date])
            
            if end_date:
                cmd.extend(['--end-date', end_date])
            
            # 记录开始时间
            start_time = time.time()
            
            self.logger.info(f"开始获取 {currency} {interval} 数据...")
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 分钟超时
                cwd=os.path.dirname(os.path.dirname(__file__))
            )
            
            # 计算执行时间
            execution_time = time.time() - start_time
            
            # 解析输出获取插入的记录数
            inserted_count = 0
            if result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if '总共插入' in line and '条 K 线数据' in line:
                        try:
                            inserted_count = int(line.split('总共插入')[1].split('条')[0].strip())
                        except:
                            pass
            
            if result.returncode == 0:
                self.logger.info(f"✅ {currency} {interval} 数据获取成功 - 插入 {inserted_count} 条记录，耗时 {execution_time:.2f}s")
                return {
                    'currency': currency,
                    'interval': interval,
                    'success': True,
                    'inserted_count': inserted_count,
                    'execution_time': execution_time,
                    'message': f'成功插入 {inserted_count} 条记录'
                }
            else:
                error_msg = result.stderr or result.stdout or '未知错误'
                self.logger.error(f"❌ {currency} {interval} 数据获取失败 - {error_msg}")
                return {
                    'currency': currency,
                    'interval': interval,
                    'success': False,
                    'inserted_count': 0,
                    'execution_time': execution_time,
                    'message': error_msg
                }
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"⏰ {currency} {interval} 数据获取超时")
            return {
                'currency': currency,
                'interval': interval,
                'success': False,
                'inserted_count': 0,
                'execution_time': 300,
                'message': '执行超时'
            }
        except Exception as e:
            self.logger.error(f"💥 {currency} {interval} 数据获取异常：{e}")
            return {
                'currency': currency,
                'interval': interval,
                'success': False,
                'inserted_count': 0,
                'execution_time': 0,
                'message': str(e)
            }
    
    def run_batch_collection(self, currencies: List[str] = None, intervals: List[str] = None,
                           days: int = None, max_workers: int = 3, 
                           start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        批量运行数据收集
        Args:
            currencies: 货币对列表，如果为 None 则使用默认列表
            intervals: 时间间隔列表，如果为 None 则使用默认列表
            days: 获取最近几天的数据，如果指定了 start_date 和 end_date 则忽略此参数
            max_workers: 最大并发数
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        Returns:
            执行结果列表
        """
        if currencies is None:
            currencies = self.currencies
        
        if intervals is None:
            intervals = self.intervals
        
        if days is None:
            days = self.default_days
        
        # 如果没有指定具体日期，则使用 days 参数
        if not start_date or not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        self.logger.info(f"🚀 开始批量数据收集")
        self.logger.info(f"货币对：{currencies}")
        self.logger.info(f"时间间隔：{intervals}")
        self.logger.info(f"时间范围：{start_date} 到 {end_date}")
        self.logger.info(f"最大并发数：{max_workers}")
        self.logger.info("=" * 60)
        
        # 生成所有任务组合
        tasks = []
        for currency in currencies:
            for interval in intervals:
                tasks.append((currency, interval, start_date, end_date))
        
        self.logger.info(f"总共 {len(tasks)} 个任务")
        
        # 执行任务
        results = []
        
        if max_workers == 1:
            # 单线程执行
            for i, (currency, interval, start_dt, end_dt) in enumerate(tasks, 1):
                self.logger.info(f"[{i}/{len(tasks)}] 处理 {currency} {interval}")
                result = self.run_offline_collector(currency, interval, start_dt, end_dt)
                results.append(result)
                
                # 避免请求过于频繁
                time.sleep(0.5)
        else:
            # 多线程执行
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任务
                future_to_task = {}
                for i, (currency, interval, start_dt, end_dt) in enumerate(tasks, 1):
                    future = executor.submit(self.run_offline_collector, currency, interval, start_dt, end_dt)
                    future_to_task[future] = (i, currency, interval)
                
                # 收集结果
                for future in concurrent.futures.as_completed(future_to_task):
                    i, currency, interval = future_to_task[future]
                    self.logger.info(f"[{i}/{len(tasks)}] 处理 {currency} {interval}")
                    
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        self.logger.error(f"任务执行异常：{e}")
                        results.append({
                            'currency': currency,
                            'interval': interval,
                            'success': False,
                            'inserted_count': 0,
                            'execution_time': 0,
                            'message': str(e)
                        })
                    
                    # 避免请求过于频繁
                    time.sleep(0.1)
        
        return results
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """打印执行结果摘要"""
        total_tasks = len(results)
        successful_tasks = len([r for r in results if r['success']])
        failed_tasks = total_tasks - successful_tasks
        total_inserted = sum(r['inserted_count'] for r in results)
        total_time = sum(r['execution_time'] for r in results)
        
        print("=" * 60)
        print("📊 执行结果摘要")
        print("=" * 60)
        print(f"总任务数：{total_tasks}")
        print(f"成功任务：{successful_tasks}")
        print(f"失败任务：{failed_tasks}")
        print(f"成功率：{successful_tasks/total_tasks*100:.1f}%")
        print(f"总插入记录数：{total_inserted}")
        print(f"总执行时间：{total_time:.2f}s")
        print(f"平均执行时间：{total_time/total_tasks:.2f}s/任务")
        
        if failed_tasks > 0:
            print("\n❌ 失败任务详情：")
            for result in results:
                if not result['success']:
                    print(f"  - {result['currency']} {result['interval']}: {result['message']}")
        
        print("=" * 60)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='批量获取离线 K 线数据')
    
    parser.add_argument('--currencies', '-c', type=str, nargs='+',
                       help='指定货币对列表，如 BTCUSDT ETHUSDT')
    
    parser.add_argument('--intervals', '-i', type=str, nargs='+',
                       help='指定时间间隔列表，如 1h 4h 1d')
    
    parser.add_argument('--days', '-d', type=int, default=7,
                       help='获取最近几天的数据 (默认：7)')
    
    parser.add_argument('--start-date', '-s', type=str,
                       help='开始日期，格式：YYYY-MM-DD')
    
    parser.add_argument('--end-date', '-e', type=str,
                       help='结束日期，格式：YYYY-MM-DD')
    
    parser.add_argument('--max-workers', '-w', type=int, default=3,
                       help='最大并发数 (默认：3)')
    
    parser.add_argument('--sequential', action='store_true',
                       help='顺序执行，不使用多线程')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='显示详细日志')
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 创建调度器
    scheduler = OfflineDataScheduler()
    
    # 处理并发数
    max_workers = 1 if args.sequential else args.max_workers
    
    try:
        # 执行批量收集
        results = scheduler.run_batch_collection(
            currencies=args.currencies,
            intervals=args.intervals,
            days=args.days,
            max_workers=max_workers,
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        # 打印结果摘要
        scheduler.print_summary(results)
        
        # 根据结果确定退出码
        failed_count = len([r for r in results if not r['success']])
        return 1 if failed_count > 0 else 0
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        return 1
    except Exception as e:
        print(f"❌ 批量数据收集失败：{e}")
        return 1


if __name__ == "__main__":
    exit(main())