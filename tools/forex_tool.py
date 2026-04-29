"""
外汇数据工具 - 免费汇率获取
使用 exchangerate-api.com (免费额度)
"""
import requests
from typing import Dict

EXCHANGE_BASE = "https://api.exchangerate-api.com/v4/latest"


class ForexTool:
    """外汇/汇率数据"""

    def __init__(self):
        self.name = "forex_tool"

    def get_rate(self, base_currency: str = "USD") -> Dict:
        """
        获取汇率（基于美元）
        常用货币: USD, EUR, GBP, JPY, CNY, HKD, AUD, CAD
        """
        try:
            url = f"{EXCHANGE_BASE}/{base_currency.upper()}"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if "rates" not in data:
                return {"error": "获取汇率失败"}
            return {
                "base": data.get("base", ""),
                "date": data.get("date", ""),
                "rates": {
                    "EUR": data["rates"].get("EUR", 0),
                    "GBP": data["rates"].get("GBP", 0),
                    "JPY": data["rates"].get("JPY", 0),
                    "CNY": data["rates"].get("CNY", 0),
                    "HKD": data["rates"].get("HKD", 0),
                    "AUD": data["rates"].get("AUD", 0),
                    "CAD": data["rates"].get("CAD", 0),
                }
            }
        except Exception as e:
            return {"error": str(e)}

    def convert(self, amount: float, from_currency: str = "USD", to_currency: str = "CNY") -> Dict:
        """货币转换"""
        try:
            url = f"{EXCHANGE_BASE}/{from_currency.upper()}"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            rate = data["rates"].get(to_currency.upper(), 0)
            return {
                "from": from_currency.upper(),
                "to": to_currency.upper(),
                "amount": amount,
                "rate": rate,
                "converted": amount * rate
            }
        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    tool = ForexTool()

    print("=== 测试 get_rate (USD基准) ===")
    print(tool.get_rate("USD"))

    print("\n=== 测试 convert (100 USD -> CNY) ===")
    print(tool.convert(100, "USD", "CNY"))
