"""
配置文件 - 所有LLM配置都在这里
"""
import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config() -> dict:
    """加载配置"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def get_llm_config() -> dict:
    """获取LLM配置"""
    config = load_config()
    llm_config = config.get("llm", {})

    return {
        "provider": config.get("llm_provider", "groq"),
        "api_key": llm_config.get("api_key", ""),
        "base_url": llm_config.get("base_url", ""),
        "model": llm_config.get("model", ""),
        "supports_function_calling": llm_config.get("supports_function_calling", False),
    }


def get_current_provider() -> str:
    """获取当前provider名称"""
    config = load_config()
    return config.get("llm_provider", "groq")
