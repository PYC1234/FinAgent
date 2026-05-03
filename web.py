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

    # 清空之前的思考
    thinking_display = ""

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
            "result_preview": str(result)[:100]
        })
        return result

    agent._execute_tool = wrapped_execute

    # 运行 Agent
    result = agent.run(message, max_steps=3)

    # 恢复原函数
    agent._execute_tool = original_execute

    # 构建思考过程展示
    thinking_parts = []
    for i, step in enumerate(steps_log, 1):
        thinking_parts.append(
            f"🔧 **Step {i}**: 调用 `{step['tool']}` ({step['time']})\n"
            f"   参数: `{json.dumps(step['args'], ensure_ascii=False)}`\n"
            f"   结果: `{step['result_preview']}...`"
        )

    if thinking_parts:
        thinking_display = "### 💭 思考过程\n\n" + "\n\n".join(thinking_parts)

    # 获取最终回答
    answer = result.get("final_answer", "处理失败")

    # 组合最终输出
    if thinking_display:
        full_output = f"{thinking_display}\n\n---\n\n### 📝 最终回答\n\n{answer}"
    else:
        full_output = answer

    return full_output


# Gradio UI
with gr.Blocks(title="FinAgent") as demo:
    gr.Markdown("""
    # 🤖 FinAgent - AI 金融分析助手

    **数据源**: 加密货币(Binance) | 美股(Twelve Data) | 外汇(Frankfurter)
    """)

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="对话",
                height=500,
                type="messages"
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
