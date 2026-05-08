"""
FinAgent Web UI - 实时显示思考过程
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
import json
import time
from agent.agent import FinAgent
from llm_client import LLMClient
from config import get_llm_config

# 自定义 CSS
CUSTOM_CSS = """
.gradio-container {
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif !important;
}
.message {
    font-size: 14px !important;
}
.thinking {
    background-color: #f0f7ff;
    border-left: 3px solid #3b82f6;
    padding: 10px;
    margin: 5px 0;
    border-radius: 4px;
}
"""


def create_agent():
    """初始化 Agent"""
    client = LLMClient()
    agent = FinAgent(client)
    try:
        with open("config.json", "r") as f:
            cfg = json.load(f)
            twelve_key = cfg.get("twelve_data_api_key")
            if twelve_key:
                agent.set_twelve_data_api_key(twelve_key)
    except Exception:
        pass
    return agent


agent = None


def init_agent():
    global agent
    if agent is None:
        agent = create_agent()
    return agent


def chat(message, history):
    """带实时思考展示的对话"""
    agent = init_agent()

    # 定义回调函数捕获思考过程
    steps_log = []
    original_execute = agent._execute_tool

    def wrapped_execute(name, arguments):
        step_start = time.time()
        result = original_execute(name, arguments)
        elapsed = time.time() - step_start
        steps_log.append({
            "tool": name,
            "args": arguments,
            "time": f"{elapsed:.1f}s",
            "result_preview": str(result)[:80]
        })
        return result

    agent._execute_tool = wrapped_execute

    # 运行 Agent
    result = agent.run(message, max_steps=3)

    # 恢复原函数
    agent._execute_tool = original_execute

    # 获取最终回答
    answer = result.get("final_answer", "处理失败")

    # 如果有工具调用，添加简洁的工具使用说明
    if steps_log:
        tool_summary = []
        for step in steps_log:
            tool_summary.append(f"📌 使用工具: `{step['tool']}` ({step['time']})")
        answer = "\n".join(tool_summary) + "\n\n" + answer

    return answer


# Gradio UI
with gr.Blocks(title="FinAgent", css=CUSTOM_CSS) as demo:
    gr.Markdown("""
    # 🤖 FinAgent - AI 金融分析助手

    **数据源**: 加密货币(Binance) | 美股(Twelve Data) | 外汇(Frankfurter)
    """)

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="对话",
                height=500,
                buttons=["copy"]
            )
            with gr.Row():
                msg = gr.Textbox(
                    label="输入问题",
                    placeholder="输入你的金融问题...",
                    scale=4,
                    container=False
                )
                submit = gr.Button("发送", variant="primary", scale=1)

        with gr.Column(scale=1):
            gr.Markdown("### 📊 快捷问题")
            example_btns = [
                gr.Button("BTC价格", size="sm"),
                gr.Button("苹果股票", size="sm"),
                gr.Button("汇率查询", size="sm"),
                gr.Button("夏普比率", size="sm"),
            ]

    # 绑定事件
    def user_input(message, history):
        """用户输入"""
        return "", history + [{"role": "user", "content": message}]

    def bot_response(history):
        """机器人回复"""
        message = history[-1]["content"]
        response = chat(message, history[:-1])
        history.append({"role": "assistant", "content": response})
        return history

    def example_click(example_text, history):
        """示例问题点击"""
        history.append({"role": "user", "content": example_text})
        response = chat(example_text, history[:-1])
        history.append({"role": "assistant", "content": response})
        return history

    # 提交
    msg.submit(
        user_input,
        [msg, chatbot],
        [msg, chatbot]
    ).then(
        bot_response,
        [chatbot],
        [chatbot]
    )

    submit.click(
        user_input,
        [msg, chatbot],
        [msg, chatbot]
    ).then(
        bot_response,
        [chatbot],
        [chatbot]
    )

    # 示例按钮
    for btn in example_btns:
        btn.click(
            example_click,
            [btn, chatbot],
            [chatbot]
        )

    gr.Markdown("""
    ---
    **数据源**: Binance | Twelve Data | Frankfurter
    **技术栈**: LLM + ReAct + RAG | GitHub: [FinAgent](https://github.com/PYC1234/FinAgent)
    """)


if __name__ == "__main__":
    print("=" * 50)
    print("FinAgent Web UI")
    print("访问 http://localhost:7860")
    print("=" * 50)
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        theme=gr.themes.Soft()
    )
