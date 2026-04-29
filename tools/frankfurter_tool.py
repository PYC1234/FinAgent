"""
Frankfurter API 工具 - 汇率数据
完全免费、开源、无需 API Key
https://www.frankfurter.app/
"""
import requests
from typing import Dict


class FrankfurterTool:
    """Frankfurter 汇率数据"""

    BASE_URL = "https://api.frankfurter.app"

    def __init__(self):
        self.name = "frankfurter_tool"

    def get_latest_rates(self, base: str = "USD") -> Dict:
        """
        获取最新汇率
        :param base: 基准货币代码，默认USD
        """
        try:
            url = f"{self.BASE_URL}/latest"
            params = {"from": base.upper()}
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if "rates" not in data:
                return {"error": "获取失败", "data": data}
            return {
                "base": data.get("base", ""),
                "date": data.get("date", ""),
                "rates": data.get("rates", {})
            }
        except Exception as e:
            return {"error": str(e)}

    def get_currencies(self) -> Dict:
        """获取所有可用货币"""
        try:
            url = f"{self.BASE_URL}/currencies"
            resp = requests.get(url, timeout=10)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def convert(self, amount: float, from_currency: str, to_currency: str) -> Dict:
        """货币转换"""
        try:
            url = f"{self.BASE_URL}/latest"
            params = {
                "from": from_currency.upper(),
                "to": to_currency.upper(),
                "amount": amount
            }
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if "rates" not in data:
                return {"error": "转换失败", "data": data}
            converted = data["rates"].get(to_currency.upper(), 0)
            # rate 是单位汇率 (1 from_currency 等于多少 to_currency)
            rate = converted / amount if amount else 0
            return {
                "from": from_currency.upper(),
                "to": to_currency.upper(),
                "amount": amount,
                "rate": rate,
                "result": converted
            }
        except Exception as e:
            return {"error": str(e)}

    def get_historical(self, date: str, base: str = "USD") -> Dict:
        """获取历史汇率"""
        try:
            url = f"{self.BASE_URL}/{date}"
            params = {"from": base.upper()}
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if "rates" not in data:
                return {"error": "获取失败", "data": data}
            return {
                "base": data.get("base", ""),
                "date": data.get("date", ""),
                "rates": data.get("rates", {})
            }
        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    tool = FrankfurterTool()

    print("=== 测试 get_latest_rates (USD) ===")
    print(tool.get_latest_rates("USD"))

    print("\n=== 测试 convert (100 USD -> EUR) ===")
    print(tool.convert(100, "USD", "EUR"))

    print("\n=== 测试 currencies ===")
    print(list(tool.get_currencies().keys())[:10])