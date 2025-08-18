#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coze Like LLM 使用示例
"""

import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.llm.coze_like import create_coze_like_llm
from core.llm.types import ELLMType


async def simple_chat_example():
    """简单的聊天示例"""
    print("🤖 Coze Like LLM 聊天示例")
    print("=" * 50)
    
    try:
        # 创建 LLM 实例
        llm = await create_coze_like_llm(ELLMType.DOUBAO_THINKING)
        print("✅ LLM 初始化成功")
        
        # 示例对话
        conversations = [
            "你好，我是一个 Python 开发者",
            "请帮我解释一下什么是机器学习",
            "能给我一些 Python 编程的建议吗？"
        ]
        
        for i, user_message in enumerate(conversations, 1):
            print(f"\n👤 用户 {i}: {user_message}")
            
            try:
                response = await llm.completions(user_message)
                print(f"🤖 助手: {response}")
                
            except Exception as e:
                print(f"❌ 对话失败：{e}")
        
        print("\n✅ 聊天示例完成")
        
    except Exception as e:
        print(f"❌ 示例运行失败：{e}")
        import traceback
        traceback.print_exc()


async def batch_processing_example():
    """批量处理示例"""
    print("\n📝 批量处理示例")
    print("=" * 50)
    
    try:
        # 创建 LLM 实例
        llm = await create_coze_like_llm(ELLMType.DOUBAO_THINKING)
        
        # 批量处理的问题列表
        questions = [
            "什么是区块链？",
            "Python 和 JavaScript 的主要区别是什么？",
            "如何提高代码质量？",
            "什么是微服务架构？",
            "如何进行有效的项目管理？"
        ]
        
        print(f"准备处理 {len(questions)} 个问题...")
        
        results = []
        for i, question in enumerate(questions, 1):
            print(f"\n处理问题 {i}/{len(questions)}: {question}")
            
            try:
                answer = await llm.completions(question)
                results.append({
                    'question': question,
                    'answer': answer,
                    'success': True
                })
                print(f"✅ 处理成功，回答长度：{len(answer)}")
                
            except Exception as e:
                results.append({
                    'question': question,
                    'answer': None,
                    'success': False,
                    'error': str(e)
                })
                print(f"❌ 处理失败：{e}")
        
        # 统计结果
        successful = len([r for r in results if r['success']])
        print(f"\n📊 批量处理完成：{successful}/{len(questions)} 个问题处理成功")
        
        return results
        
    except Exception as e:
        print(f"❌ 批量处理示例失败：{e}")
        return []


async def main():
    """主函数"""
    print("🚀 Coze Like LLM 使用示例")
    print("=" * 60)
    
    # 运行示例
    await simple_chat_example()
    await batch_processing_example()
    
    print("\n🎉 所有示例运行完成！")


if __name__ == "__main__":
    asyncio.run(main())
