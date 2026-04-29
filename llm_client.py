"""
LLM客户端
"""
import requests
from typing import List, Dict, Optional, Union
from config import get_llm_config, get_current_provider


class LLMClient:
    """LLM客户端"""

    def __init__(self):
        config = get_llm_config()

        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "")
        self.model = config.get("model", "")
        self.supports_function_calling = config.get("supports_function_calling", False)
        self.provider_name = get_current_provider()

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        tools: Optional[List[Dict]] = None,
        max_retries: int = 2
    ) -> Union[str, Dict]:
        """发送对话请求"""
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        # 智谱特殊处理
        if self.provider_name == "zhipu":
            payload["thinking"] = {"type": "disabled"}

            # 智谱的 tools 格式可能不同，尝试简化
            if tools:
                # 简化为只传必要的工具
                formatted_tools = []
                for tool in tools[:3]:  # 只传前3个工具测试
                    if "function" in tool:
                        formatted_tools.append({
                            "type": "function",
                            "function": {
                                "name": tool["function"]["name"],
                                "description": tool["function"].get("description", ""),
                            }
                        })
                if formatted_tools:
                    payload["tools"] = formatted_tools
                    payload["tool_choice"] = "auto"
        else:
            if tools and self.supports_function_calling:
                payload["tools"] = tools
                payload["tool_choice"] = "auto"

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                resp = requests.post(url, json=payload, headers=self.headers, timeout=60)
                resp.raise_for_status()
                data = resp.json()

                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    message = choice.get("message", {})

                    if "tool_calls" in message and self.supports_function_calling:
                        return data
                    elif "content" in message and message["content"]:
                        return message["content"]

                return str(data)

            except requests.exceptions.Timeout:
                last_error = "请求超时"
            except requests.exceptions.RequestException as e:
                last_error = f"API请求失败: {str(e)}"
            except Exception as e:
                last_error = f"未知错误: {str(e)}"

        return f"Error: {last_error}（已重试{max_retries}次）"

    def chat_simple(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """简单对话"""
        result = self.chat(messages, temperature)
        if isinstance(result, dict):
            return str(result)
        return result
