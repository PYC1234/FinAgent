"""
FinAgent - 金融分析Agent
支持 Function Calling / ReAct 双模式
"""
import json
import pandas as pd
import re
from typing import Dict, List, Any, Optional
from tools.crypto_tool import CryptoTool
from tools.alpha_vantage_tool import AlphaVantageTool
from tools.forex_tool import ForexTool
from tools.frankfurter_tool import FrankfurterTool
from tools.twelve_data_tool import TwelveDataTool
from tools.analysis_tool import AnalysisTool
from rag.retriever import Retriever
from llm_client import LLMClient


class FinAgent:
    """金融分析Agent"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.crypto_tool = CryptoTool()
        self.alpha_vantage_tool = AlphaVantageTool()
        self.forex_tool = ForexTool()
        self.frankfurter_tool = FrankfurterTool()
        self.twelve_data_tool = TwelveDataTool()
        self.analysis_tool = AnalysisTool()
        self.retriever = Retriever()
        self.llm = llm_client
        # 对话历史（支持多轮对话）
        self.messages = []
        self.query = ""  # 当前问题

        # 工具注册
        self.tools = {
            "get_crypto_price": self.crypto_tool.get_price,
            "get_crypto_24h": self.crypto_tool.get_24h_stats,
            "get_crypto_klines": self.crypto_tool.get_klines,
            # Alpha Vantage (有限制)
            "get_alpha_quote": self.alpha_vantage_tool.get_quote,
            "get_alpha_daily": self.alpha_vantage_tool.get_daily,
            "get_fx_rate": self.alpha_vantage_tool.get_fx_rate,
            # Forex
            "get_forex_rate": self.forex_tool.get_rate,
            "convert_currency": self.forex_tool.convert,
            # Frankfurter (免费外汇)
            "get_frankfurter_rates": self.frankfurter_tool.get_latest_rates,
            "convert_frankfurter": self.frankfurter_tool.convert,
            # Twelve Data (美股，800 credits/天)
            "get_twelve_data_quote": self.twelve_data_tool.get_quote,
            "get_twelve_data_earnings": self.twelve_data_tool.get_earnings,
            "get_twelve_data_profile": self.twelve_data_tool.get_stock_profile,
            # 分析工具
            "analyze_summary": self._wrap_analyze_summary,
            "analyze_compare": self._wrap_analyze_compare,
            "search_knowledge": self._search_knowledge,
        }

        # 工具Schema
        self.tools_schema = [
            # 加密货币
            {
                "type": "function",
                "function": {
                    "name": "get_crypto_price",
                    "description": "获取加密货币当前价格",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "交易对，如BTCUSDT、ETHUSDT"}
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_crypto_24h",
                    "description": "获取加密货币24小时统计数据",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "交易对，如BTCUSDT"}
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_crypto_klines",
                    "description": "获取加密货币K线数据",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "交易对"},
                            "interval": {"type": "string", "description": "时间间隔，如1h, 1d"},
                            "limit": {"type": "integer", "description": "数据条数"}
                        },
                        "required": ["symbol"]
                    }
                }
            },
            # Alpha Vantage (有限制)
            {
                "type": "function",
                "function": {
                    "name": "get_alpha_quote",
                    "description": "获取美股实时报价（Alpha Vantage，有限制）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "股票代码"}
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_fx_rate",
                    "description": "获取汇率（Alpha Vantage）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "from_currency": {"type": "string", "description": "源货币"},
                            "to_currency": {"type": "string", "description": "目标货币"}
                        },
                        "required": ["from_currency", "to_currency"]
                    }
                }
            },
            # Forex
            {
                "type": "function",
                "function": {
                    "name": "get_forex_rate",
                    "description": "获取汇率（基于美元）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "base_currency": {"type": "string", "description": "基准货币，默认USD"}
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "convert_currency",
                    "description": "货币转换",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {"type": "number", "description": "金额"},
                            "from_currency": {"type": "string", "description": "源货币"},
                            "to_currency": {"type": "string", "description": "目标货币"}
                        },
                        "required": ["amount", "from_currency", "to_currency"]
                    }
                }
            },
            # Frankfurter (免费外汇)
            {
                "type": "function",
                "function": {
                    "name": "get_frankfurter_rates",
                    "description": "获取汇率（Frankfurter免费，无需Key）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "base": {"type": "string", "description": "基准货币代码，默认USD"}
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "convert_frankfurter",
                    "description": "货币转换（Frankfurter）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {"type": "number", "description": "金额"},
                            "from_currency": {"type": "string", "description": "源货币"},
                            "to_currency": {"type": "string", "description": "目标货币"}
                        },
                        "required": ["amount", "from_currency", "to_currency"]
                    }
                }
            },
            # Twelve Data (美股，800 credits/天)
            {
                "type": "function",
                "function": {
                    "name": "get_twelve_data_quote",
                    "description": "获取美股实时报价（Twelve Data，800credits/天）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "股票代码，如AAPL、TSLA、MSFT"}
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_twelve_data_earnings",
                    "description": "获取美股财报数据（Twelve Data）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "股票代码"}
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_twelve_data_profile",
                    "description": "获取美股公司概要（Twelve Data）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "股票代码"}
                        },
                        "required": ["symbol"]
                    }
                }
            },
            # 分析工具
            {
                "type": "function",
                "function": {
                    "name": "analyze_summary",
                    "description": "计算分析指标",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prices_data": {"type": "string", "description": "价格列表JSON"},
                            "name": {"type": "string", "description": "资产名称"}
                        },
                        "required": ["prices_data", "name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_compare",
                    "description": "对比多资产表现",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "price_dict": {"type": "string", "description": "多资产价格JSON"}
                        },
                        "required": ["price_dict"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge",
                    "description": "检索金融知识",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "查询关键词"}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    def set_twelve_data_api_key(self, api_key: str):
        """设置 Twelve Data API Key"""
        self.twelve_data_tool.set_api_key(api_key)

    def _wrap_analyze_summary(self, **kwargs) -> Dict:
        prices_data = kwargs.get("prices_data", "[]")
        name = kwargs.get("name", "Asset")
        try:
            if isinstance(prices_data, str):
                prices_data = json.loads(prices_data)
            series = pd.Series(prices_data)
            return self.analysis_tool.summary(series, name)
        except Exception as e:
            return {"error": str(e)}

    def _wrap_analyze_compare(self, **kwargs) -> Dict:
        price_dict = kwargs.get("price_dict", "{}")
        try:
            if isinstance(price_dict, str):
                price_dict = json.loads(price_dict)
            result = {}
            for name, prices in price_dict.items():
                if isinstance(prices, list):
                    series = pd.Series(prices)
                    result[name] = self.analysis_tool.summary(series, name)
            return result
        except Exception as e:
            return {"error": str(e)}

    def _search_knowledge(self, **kwargs) -> str:
        return self.retriever.retrieve(kwargs.get("query", ""))

    def _execute_tool(self, name: str, arguments: Dict) -> Dict:
        if name not in self.tools:
            return {"error": f"未知工具: {name}"}
        try:
            return self.tools[name](**arguments)
        except Exception as e:
            return {"error": str(e)}

    def _parse_text_action(self, content: str) -> Optional[Dict]:
        """解析文字版 Action 格式（ReAct 兼容）"""
        action_pattern = r"Action:\s*(\w+)\s*(?:\((.*?)\))?"
        match = re.search(action_pattern, content, re.DOTALL)
        if not match:
            return None

        tool_name = match.group(1)
        args_str = match.group(2) or "{}"

        try:
            if args_str.strip():
                args = json.loads(args_str)
            else:
                args = {}
        except json.JSONDecodeError:
            args = {}
            kv_pattern = r'(\w+)="([^"]*)"'
            for m in re.findall(kv_pattern, args_str):
                args[m[0]] = m[1]

        return {"name": tool_name, "args": args}

    def run(self, query: str, max_steps: int = 5) -> Dict[str, Any]:
        if self.llm is None:
            return {"query": query, "final_answer": "错误：LLM未初始化"}

        self.query = query  # 保存当前问题

        # 如果是对话刚开始，添加系统提示
        if not self.messages:
            self.messages.append({
                "role": "system",
                "content": """你是一个专业的金融分析助手，擅长使用工具获取实时数据。

可用工具：
【加密货币 - Binance】
- get_crypto_price: 获取币种当前价格
- get_crypto_24h: 获取24小时统计
- get_crypto_klines: 获取K线数据

【美股 - Twelve Data】(推荐，800 credits/天)
- get_twelve_data_quote: 股票实时报价
- get_twelve_data_earnings: 财报数据
- get_twelve_data_profile: 公司概要

【外汇 - Frankfurter】(免费无需Key)
- get_frankfurter_rates: 获取汇率
- convert_frankfurter: 货币转换

【分析工具】
- analyze_summary, analyze_compare

【知识库】
- search_knowledge

规则：
1. 先理解问题，选择合适的工具
2. 如果需要数据，调用工具获取
3. 分析数据后给出结论
4. 如果用户要求继续分析，继续获取数据"""
            })

        # 添加用户问题
        self.messages.append({"role": "user", "content": query})

        response = {"query": query, "steps": [], "final_answer": None}

        for step in range(max_steps):
            print(f"\n{'='*50}")
            print(f"🔄 步骤 {step + 1}/{max_steps} - 思考中...")
            print(f"{'='*50}")

            llm_response = self.llm.chat(self.messages, tools=self.tools_schema)

            if isinstance(llm_response, str):
                if llm_response.startswith("Error:"):
                    response["final_answer"] = llm_response
                    return response
                print(f"\n💭 思考: {llm_response[:200]}...")
                response["final_answer"] = llm_response
                break

            if not isinstance(llm_response, dict):
                continue

            try:
                choice = llm_response.get("choices", [{}])[0]
                message = choice.get("message", {})

                content = message.get("content", "")
                if content:
                    print(f"\n💭 思考: {content}")

                tool_calls = message.get("tool_calls", [])
                action_info = None

                if not tool_calls and content:
                    action_info = self._parse_text_action(content)

                if not tool_calls and not action_info:
                    if content:
                        response["final_answer"] = content
                    break

                if action_info:
                    func_name = action_info["name"]
                    args = action_info["args"]
                    print(f"\n🎯 行动: 调用工具 [{func_name}] (文字解析)")
                    print(f"   参数: {args}")

                    result = self._execute_tool(func_name, args)
                    print(f"   结果: {str(result)[:150]}...")

                    response["steps"].append({
                        "thought": content or "分析中...",
                        "tool": func_name,
                        "args": args,
                        "result": result
                    })

                    self.messages.append({"role": "assistant", "content": content})
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": "text_action",
                        "content": json.dumps(result, ensure_ascii=False, default=str)
                    })
                else:
                    for tool_call in tool_calls:
                        func_name = tool_call["function"]["name"]
                        args = json.loads(tool_call["function"]["arguments"])
                        print(f"\n🎯 行动: 调用工具 [{func_name}]")
                        print(f"   参数: {args}")

                        result = self._execute_tool(func_name, args)
                        print(f"   结果: {str(result)[:150]}...")

                        response["steps"].append({
                            "thought": content or "分析中...",
                            "tool": func_name,
                            "args": args,
                            "result": result
                        })

                        self.messages.append({"role": "assistant", "content": content, "tool_calls": [tool_call]})
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.get("id", ""),
                            "content": json.dumps(result, ensure_ascii=False, default=str)
                        })

                self.messages.append({"role": "user", "content": "基于以上工具结果继续分析，如果数据足够请给出最终结论。"})

            except Exception as e:
                print(f"[Debug] 异常: {e}")
                continue

        return self._format_response(response)

    def _format_response(self, response: Dict) -> Dict:
        lines = []
        lines.append("=" * 60)
        lines.append("📊 FinAgent 金融分析报告")
        lines.append("=" * 60)
        lines.append(f"\n问题: {response['query']}")

        if response["steps"]:
            lines.append("\n📋 分析过程:")
            for i, s in enumerate(response["steps"], 1):
                thought = s.get("thought", "")
                if thought:
                    lines.append(f"  Step {i}: 💭 {thought[:80]}...")
                lines.append(f"        🎯 工具: {s['tool']}")
                lines.append(f"        📥 结果: {str(s['result'])[:100]}")

        if response["final_answer"]:
            lines.append("\n" + "-" * 40)
            lines.append("📝 最终结论:")
            lines.append("-" * 40)
            lines.append(str(response["final_answer"]))

        lines.append("\n" + "=" * 60)
        response["final_answer"] = "\n".join(lines)
        return response


if __name__ == "__main__":
    print("请通过 main.py 启动")