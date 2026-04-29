"""
Twelve Data 工具 - 美股数据
免费额度: 800 credits/天
需要 API Key: https://twelvedata.com/
"""
import requests
from typing import Dict, Optional


class TwelveDataTool:
    """Twelve Data 美股数据"""

    BASE_URL = "https://api.twelvedata.com"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ""
        self.name = "twelve_data_tool"

    def set_api_key(self, api_key: str):
        """设置 API Key"""
        self.api_key = api_key

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """发送请求"""
        if not self.api_key:
            return {"error": "需要 API Key"}
        url = f"{self.BASE_URL}/{endpoint}"
        params = params or {}
        params["apikey"] = self.api_key
        try:
            resp = requests.get(url, params=params, timeout=15)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def get_quote(self, symbol: str = "AAPL") -> Dict:
        """
        获取股票实时报价
        :param symbol: 股票代码，如AAPL、TSLA、MSFT
        """
        data = self._make_request("quote", {"symbol": symbol})
        if "Error Message" in data:
            return {"error": data["Error Message"], "symbol": symbol}
        if "status" in data and data["status"] != "ok":
            return {"error": data.get("message", "请求失败"), "symbol": symbol}
        return {
            "symbol": data.get("symbol", ""),
            "name": data.get("name", ""),
            "price": float(data.get("close", 0)),
            "change": float(data.get("change", 0)),
            "change_pct": float(data.get("percent_change", 0)),
            "high": float(data.get("high", 0)),
            "low": float(data.get("low", 0)),
            "open": float(data.get("open", 0)),
            "prev_close": float(data.get("previous_close", 0)),
            "volume": int(data.get("volume", 0)),
            "exchange": data.get("exchange", ""),
            "currency": data.get("currency", ""),
            "fifty_two_week_high": float(data.get("fifty_two_week", {}).get("high", 0)),
            "fifty_two_week_low": float(data.get("fifty_two_week", {}).get("low", 0)),
        }

    def get_earnings(self, symbol: str = "AAPL") -> Dict:
        """获取财报数据"""
        data = self._make_request("earnings", {"symbol": symbol})
        if "Error Message" in data:
            return {"error": data["Error Message"], "symbol": symbol}
        return data

    def get_stock_profile(self, symbol: str = "AAPL") -> Dict:
        """获取股票概要"""
        data = self._make_request("stock_profile", {"symbol": symbol})
        if "Error Message" in data:
            return {"error": data["Error Message"], "symbol": symbol}
        return data


if __name__ == "__main__":
    key = "ec184bc37c55438fa20b6702e22d732a"
    tool = TwelveDataTool(key)

    print("=== 测试 get_quote (AAPL) ===")
    print(tool.get_quote("AAPL"))

    print("\n=== 测试 get_quote (TSLA) ===")
    print(tool.get_quote("TSLA"))

    print("\n=== 测试 get_quote (MSFT) ===")
    print(tool.get_quote("MSFT"))