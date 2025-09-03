#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 LLM 生成 Backtrader 策略并批量回测入库。

功能概述：
1) 使用 core/llm/coze_like.py 并行生成策略代码（支持配置多个 ELLMType）
2) 以 YYYY-MM-DD_HH:mm:ss_XXXX.py（XXXX 为 4 位随机数）命名保存到 back-test/strategy
3) 参考 data-collector/get_offline.py 的 currency 与 interval 组合，
   通过子进程运行 back-test/index.py 执行回测
4) 将回测结果写入 MySQL 表 strategy（核心指标直存，其他指标放入 extra）

示例：
python3 back-test/llm-strategy.py --models deepseek0528 --max-workers 2
"""

import sys
import os
import re
import json
import time
import argparse
import random
import logging
import asyncio
import concurrent.futures
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import subprocess

# 将项目根目录加入路径，便于导入
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from core.llm.types import ELLMType
from core.llm.coze_like import create_coze_like_llm
from core.llm.prompt.strategy import generate_strategy
from core.mysql.strategy import create_strategy as db_create_strategy


def _setup_logger() -> logging.Logger:
    logger = logging.getLogger('LLMStrategyOrchestrator')
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(ch)
    return logger


LOGGER = _setup_logger()


# 默认的币种与时间间隔（参考 data-collector/get_offline.py）
DEFAULT_CURRENCIES = [
    'BTCUSDT', 
    'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
    'SOLUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'LINKUSDT'
]

DEFAULT_INTERVALS = [
    '5m',
    '15m', '30m', '1h', '4h', '1d'
  ]

# 默认模型数组，便于后续集中调整
DEFAULT_MODELS: List[ELLMType] = [ELLMType.DEEPSEEK0528]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='使用 LLM 生成策略并批量回测入库')
    parser.add_argument('--models', '-m', type=str, nargs='+',
                        help='要使用的模型列表，对应 ELLMType 的 value，例如 deepseek0528 doubao15pro')
    parser.add_argument('--currencies', '-c', type=str, nargs='+',
                        help='币种列表，默认同 data-collector/get_offline.py')
    parser.add_argument('--intervals', '-i', type=str, nargs='+',
                        help='时间间隔列表，默认同 data-collector/get_offline.py')
    parser.add_argument('--max-workers', '-w', type=int, default=1,
                        help='并发回测的最大子进程数（默认 2）')
    parser.add_argument('--sequential', action='store_true',
                        help='回测顺序执行（不并发）')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='详细日志')
    return parser.parse_args()


def resolve_llm_types(model_values: Optional[List[str]]) -> List[ELLMType]:
    """根据传入的字符串列表解析为 ELLMType 列表。未指定则默认 [ELLMType.DEEPSEEK0528]。"""
    if not model_values:
        return list(DEFAULT_MODELS)

    value_to_enum = {e.value: e for e in ELLMType}
    selected: List[ELLMType] = []
    for v in model_values:
        enum_obj = value_to_enum.get(v)
        if enum_obj:
            selected.append(enum_obj)
        else:
            LOGGER.warning(f'未识别的模型：{v}, 已跳过')
    return selected or list(DEFAULT_MODELS)


def ensure_strategy_dir() -> str:
    strategy_dir = os.path.join(os.path.dirname(__file__), 'strategy')
    os.makedirs(strategy_dir, exist_ok=True)
    return strategy_dir


def generate_strategy_filename() -> Tuple[str, str]:
    """生成符合要求的文件名和不带扩展名的策略名。格式：YYYY-MM-DD_HH:mm:ss_XXXX.py"""
    ts = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    rnd = random.randint(0, 9999)
    name_no_ext = f"{ts}_{rnd:04d}"
    return name_no_ext + '.py', name_no_ext


def normalize_strategy_code(raw: str) -> str:
    """对 LLM 结果做适配：
    - 去除 markdown 代码围栏
    - 删除 print 行
    - 若无 class Strategy，尝试将 class LLMStrategy 别名为 Strategy
    - 确保 import backtrader as bt 存在
    """
    # 去掉围栏
    lines = [ln for ln in raw.splitlines() if not ln.strip().startswith('```')]
    # 删除 print 行（简单处理）
    filtered: List[str] = []
    for ln in lines:
        if re.match(r'^\s*print\s*\(.*\)\s*$', ln):
            continue
        filtered.append(ln)

    code = '\n'.join(filtered).strip()

    if 'import backtrader as bt' not in code:
        code = 'import backtrader as bt\n' + code

    # 如果没有 Strategy 类但有 LLMStrategy，则添加别名
    if 'class Strategy(' not in code and 'class LLMStrategy(' in code:
        code += '\n\n# Engine adapter\ntry:\n    Strategy\nexcept NameError:\n    try:\n        Strategy = LLMStrategy\n    except NameError:\n        pass\n'

    return code + '\n'


async def call_single_llm(model: ELLMType, prompt: str) -> Tuple[ELLMType, str]:
    llm = await create_coze_like_llm(model)
    result = await llm.completions(prompt)
    print(result)
    return model, result


async def generate_strategies_in_parallel(models: List[ELLMType], prompt: str) -> List[Tuple[ELLMType, str]]:
    tasks = [call_single_llm(m, prompt) for m in models]
    results: List[Tuple[ELLMType, str]] = await asyncio.gather(*tasks, return_exceptions=False)
    return results


def save_strategy_file(content: str) -> Tuple[str, str]:
    strategy_dir = ensure_strategy_dir()
    filename, name_no_ext = generate_strategy_filename()
    path = os.path.join(strategy_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    LOGGER.info(f'策略已保存：{path}')
    return path, name_no_ext


def run_backtest_subprocess(currency: str, interval: str, strategy_name: str) -> Optional[Dict[str, Any]]:
    """调用 back-test/index.py 执行回测，返回解析后的结果字典。失败返回 None。"""
    index_script = os.path.join(os.path.dirname(__file__), 'index.py')
    cmd = [
        'python3', index_script,
        '--currency', currency,
        '--time_interval', interval,
        '--strategy_name', strategy_name
    ]

    LOGGER.info(f'开始回测：{cmd}')
    start_t = time.time()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
            cwd=PROJECT_ROOT
        )
    except subprocess.TimeoutExpired:
        LOGGER.error(f'回测超时：{currency} {interval} {strategy_name}')
        return None
    except Exception as e:
        LOGGER.error(f'回测异常：{currency} {interval} {strategy_name} - {e}')
        return None

    elapsed = time.time() - start_t
    stdout = proc.stdout or ''
    stderr = proc.stderr or ''

    if proc.returncode != 0:
        LOGGER.error(f'回测失败 [{proc.returncode}]: {currency} {interval} {strategy_name} - {stderr or stdout}')
        return None

    # 从分割线提取 JSON（index.py 会在 JSON 前打印一行分割线）
    LOGGER.info(f'回测结果：{stdout}')
    sep = '==============================================='
    idx = stdout.rfind(sep)
    json_text = stdout[idx + len(sep):].strip() if idx != -1 else ''
    try:
        data = json.loads(json_text)
        if isinstance(data, dict):
            data['execution_time'] = elapsed
            return data
    except Exception:
        LOGGER.error(f'回测结果解析失败：{currency} {interval} {strategy_name}')
        return None

    return None


def persist_strategy_result(strategy_name: str, llm_type: ELLMType, result: Dict[str, Any], strategy_content: str = "") -> Optional[int]:
    """将回测结果写入 strategy 表。返回新记录 ID。"""
    try:
        currency = result.get('currency')
        interval = result.get('time_interval')
        
        # 检查 sharpe_ratio 是否大于 0 并且有实际交易
        sharpe_ratio = result.get('sharpe_ratio')
        trades = result.get('trades', [])
        trade_count = result.get('trade_count', 0)
        
        if sharpe_ratio is None or sharpe_ratio <= 0:
            LOGGER.info(f'策略 {strategy_name} 的 sharpe_ratio ({sharpe_ratio}) <= 0，跳过入库 [{currency} {interval}]')
            return None
            
        # 检查是否有实际交易记录
        if not trades or trade_count <= 0:
            LOGGER.info(f'策略 {strategy_name} 无实际交易记录 (trades={len(trades)}, trade_count={trade_count})，跳过入库 [{currency} {interval}]')
            return None

        # trades 作为 JSON 字符串保存
        trades_json = json.dumps(result.get('trades', []), ensure_ascii=False)

        # 如果没有传入策略内容，尝试从文件读取
        if not strategy_content:
            try:
                strategy_dir = ensure_strategy_dir()
                strategy_file_path = os.path.join(strategy_dir, f"{strategy_name}.py")
                if os.path.exists(strategy_file_path):
                    with open(strategy_file_path, 'r', encoding='utf-8') as f:
                        strategy_content = f.read()
                    LOGGER.info(f'成功读取策略文件内容：{strategy_file_path}')
                else:
                    LOGGER.warning(f'策略文件不存在：{strategy_file_path}')
            except Exception as e:
                LOGGER.error(f'读取策略文件内容失败：{e}')

        # 额外指标放入 extra
        extra_payload = {
            'total_return': result.get('total_return'),
            'annual_return': result.get('annual_return'),
            'calmar_ratio': result.get('calmar_ratio'),
            'vwr': result.get('vwr'),
            'data_points': result.get('data_points'),
            'start_date': result.get('start_date'),
            'end_date': result.get('end_date'),
            'llm_type': llm_type.value,
        }

        data = {
            'name': strategy_name,
            'currency': currency,
            'time_interval': interval,
            'sharpe_ratio': result.get('sharpe_ratio'),
            'trade_count': result.get('trade_count'),
            'trades': trades_json,
            'total_commission': result.get('total_commission'),
            'max_drawdown': result.get('max_drawdown'),
            'winning_percentage': result.get('winning_percentage'),
            'reason': f'auto-generated by {llm_type.value}',
            'init_balance': result.get('init_balance'),
            'final_balance': result.get('final_balance'),
            'extra': json.dumps(extra_payload, ensure_ascii=False),
            'content': strategy_content,
            'model': llm_type.value
        }

        new_id = db_create_strategy(data)
        LOGGER.info(f'回测结果入库成功，ID={new_id} [{currency} {interval}]')
        return new_id
    except Exception as e:
        LOGGER.error(f'回测结果入库失败：{e}')
        return None


def run_batch_backtests(strategy_name: str, llm_type: ELLMType,
                        currencies: List[str], intervals: List[str],
                        max_workers: int, strategy_content: str = "") -> None:
    tasks: List[Tuple[str, str]] = [(c, i) for c in currencies for i in intervals]
    LOGGER.info(f'开始批量回测：{len(tasks)} 组 [{strategy_name}]')

    def worker(job: Tuple[str, str]) -> None:
        ccy, itv = job
        res = run_backtest_subprocess(ccy, itv, strategy_name)
        if res and 'error' not in res:
            result_id = persist_strategy_result(strategy_name, llm_type, res, strategy_content)
            if result_id:
                LOGGER.info(f'策略入库成功：{ccy} {itv} [{strategy_name}] -> ID={result_id}')
            else:
                LOGGER.info(f'策略未入库（sharpe_ratio <= 0 或无交易记录）：{ccy} {itv} [{strategy_name}]')
        else:
            LOGGER.warning(f'回测无结果/失败：{ccy} {itv} [{strategy_name}]')

    if max_workers <= 1:
        for job in tasks:
            worker(job)
            time.sleep(0.1)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(worker, tasks))


async def main_async(args: argparse.Namespace) -> int:
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    currencies = args.currencies or DEFAULT_CURRENCIES
    intervals = args.intervals or DEFAULT_INTERVALS
    models = resolve_llm_types(args.models)

    LOGGER.info(f'模型：{[m.value for m in models]}')
    LOGGER.info(f'币种：{currencies}')
    LOGGER.info(f'间隔：{intervals}')

    # 1) 并行生成策略
    LOGGER.info('开始并行生成策略代码...')
    llm_results = await generate_strategies_in_parallel(models, generate_strategy)

    # 2) 逐个保存并回测
    for llm_type, raw_code in llm_results:
        try:
            code = normalize_strategy_code(raw_code)
            path, name_no_ext = save_strategy_file(code)
            LOGGER.info(f'生成策略 [{llm_type.value}] -> {os.path.basename(path)}')

            # 3) 批量回测入库
            max_workers = 1 if args.sequential else max(1, args.max_workers)
            run_batch_backtests(name_no_ext, llm_type, currencies, intervals, max_workers, code)
        except Exception as e:
            LOGGER.error(f'处理策略 [{llm_type.value}] 失败：{e}')

    LOGGER.info('全部处理完成')
    return 0


def main() -> int:
    args = parse_args()
    return asyncio.run(main_async(args))


if __name__ == '__main__':
    sys.exit(main())

