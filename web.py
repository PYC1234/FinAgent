"""
FinAgent Web UI - Gradio Chat Interface
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
import json
from agent.agent import FinAgent
from llm_client import LLMClient
from config import get_llm_config


def create_agent():
    """初始化 Agent"""
    client = LLMClient()
    agent = FinAgent(client)

    # 设置 Twelve Data API Key
    try:
        with open("config.json", "r") as f:
            cfg = json.load(f)
            twelve_key = cfg.get("twelve_data_api_key")
            if twelve_key:
                agent.set_twelve_data_api_key(twelve_key)
    except Exception:
        pass

    return agent


# 全局 Agent 实例
agent = None


def init_agent():
    global agent
    if agent is None:
        agent = create_agent()
    return agent


def chat(message, history):
    """Gradio 对话回调"""
    agent = init_agent()

    # 调用 Agent
    result = agent.run(message)

    # 返回最终回答
    answer = result.get("final_answer", "处理失败")

    # 同时返回分析过程作为思考展示
    steps = result.get("steps", [])
    thinking = ""
    if steps:
        thinking_lines = []
        for i, s in enumerate(steps, 1):
            thought = s.get("thought", "")
            if thought:
                thinking_lines.append(f"Step {i}: {thought[:100]}")
        if thinking_lines:
            thinking = "\n".join(thinking_lines)

    # 在回答前附加思考过程
    if thinking:
        full_answer = f"💭 **思考过程**:\n{thinking}\n\n---\n\n{answer}"
    else:
        full_answer = answer

    return full_answer


# Gradio Chat Interface
with gr.Blocks(title="FinAgent", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🤖 FinAgent - AI 金融分析助手

    **支持**: 加密货币 | 美股 | 外汇 | 金融知识问答

    > 输入你的问题，Agent 会自动调用工具并分析
    """)

    chatbot = gr.ChatInterface(
        fn=chat,
        title="",
        description="",
        examples=[
            "BTC现在价格多少？",
            "苹果最近走势如何？",
            "100美元等于多少人民币？",
            "夏普比率是什么？",
            "比较一下ETH和特斯拉"
        ],
        cache_examples=False,
        retry_btn="🔄 重新生成",
        undo_btn="↩️ 撤销",
        clear_btn="🗑️ 清除对话",
    )

    gr.Markdown("""
    ---
    **数据源**: Binance(加密货币) | Twelve Data(美股) | Frankfurter(外汇)
    **技术栈**: LLM驱动 + ReAct架构 + RAG知识检索
    """)


if __name__ == "__main__":
    print("=" * 50)
    print("启动 FinAgent Web UI...")
    print("访问 http://localhost:7860")
    print("=" * 50)
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
