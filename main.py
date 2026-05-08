"""
FinAgent 主入口
"""
import sys
import os
import json as json_module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.agent import FinAgent
from llm_client import LLMClient
from config import get_llm_config, get_current_provider


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    FinAgent v1.0                              ║
║              多资产金融分析智能Agent系统                        ║
║                                                              ║
║  🔮 LLM驱动的ReAct Agent                                     ║
║  📊 数据源: Crypto(Binance) | Forex(Frankfurter)             ║
║            美股(Twelve Data) | 知识库(RAG)                     ║
╚══════════════════════════════════════════════════════════════╝
    """)


def setup_llm():
    """从config.json初始化LLM"""
    config = get_llm_config()
    provider = get_current_provider()

    api_key = config.get("api_key", "")
    if not api_key or api_key.startswith("your-"):
        print("❌ 未配置API Key")
        print("\n请在 config.json 中配置：")
        print("-" * 50)
        print("""
{
  "llm_provider": "siliconflow",
  "llm": {
    "api_key": "你的API Key",
    "base_url": "https://api.siliconflow.cn/v1",
    "model": "deepseek-ai/DeepSeek-V3",
    "supports_function_calling": true
  },
  "twelve_data_api_key": "你的Twelve Data Key"
}
""")
        print("-" * 50)
        return None

    client = LLMClient()
    print(f"✓ 使用: {provider}")
    print(f"✓ 模型: {config.get('model')}")
    print(f"✓ Function Calling: {'支持' if config.get('supports_function_calling') else '不支持'}")
    return client


def test_connection(client: LLMClient) -> bool:
    print("\n🔗 测试连接...")
    result = client.chat_simple([{"role": "user", "content": "hi"}])
    if not result.startswith("Error:"):
        print("✓ 连接成功！")
        return True
    print(f"⚠ 连接失败: {result}")
    return False


def interactive(agent: FinAgent):
    print("\n💬 交互模式 (quit退出)\n")
    while True:
        try:
            q = input("你: ").strip()
            if q.lower() in ["quit", "exit", "q"]:
                break
            if not q:
                continue

            print("\n🔍 分析中...\n")
            result = agent.run(q)
            print(result["final_answer"])
            print()

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ 错误: {e}\n")


def main():
    print_banner()

    client = setup_llm()
    if not client:
        return

    if not test_connection(client):
        return

    agent = FinAgent(client)

    # 设置 Twelve Data API Key
    try:
        with open("config.json", "r") as f:
            cfg = json_module.load(f)
            twelve_key = cfg.get("twelve_data_api_key")
            if twelve_key:
                agent.set_twelve_data_api_key(twelve_key)
                print(f"✓ Twelve Data API Key 已设置")
    except Exception:
        pass

    interactive(agent)


if __name__ == "__main__":
    main()
