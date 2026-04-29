"""
Alpha Vantage 工具 - 股票、外汇、加密货币数据
需要 API Key: https://www.alphavantage.co/support#api-key
"""
import requests
from typing import Dict, Optional

ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"


class AlphaVantageTool:
    """Alpha Vantage 数据获取"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "demo"  # demo 有限速
        self.name = "alpha_vantage_tool"

    def get_quote(self, symbol: str = "IBM") -> Dict:
        """获取股票实时报价"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        try:
            resp = requests.get(ALPHA_VANTAGE_BASE, params=params, timeout=10)
            data = resp.json()
            if "Global Quote" in data and data["Global Quote"]:
                q = data["Global Quote"]
                return {
                    "symbol": q.get("01. symbol", ""),
                    "price": float(q.get("05. price", 0)),
                    "change_pct": float(q.get("10. change percent", "0").replace("%", "")),
                    "high": float(q.get("03. high", 0)),
                    "low": float(q.get("04. low", 0)),
                    "volume": int(q.get("06. volume", 0)),
                }
            return {"error": data.get("Note", "获取失败"), "symbol": symbol}
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def get_daily(self, symbol: str = "IBM", output_size: str = "compact") -> Dict:
        """获取日线历史数据"""
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": output_size,  # compact=100天, full=20年
            "apikey": self.api_key
        }
        try:
            resp = requests.get(ALPHA_VANTAGE_BASE, params=params, timeout=10)
            data = resp.json()
            if "Time Series (Daily)" in data:
                ts = data["Time Series (Daily)"]
                dates = sorted(ts.keys(), reverse=True)[:30]
                return {
                    "symbol": symbol,
                    "dates_count": len(ts),
                    "latest_date": dates[0],
                    "latest_close": float(ts[dates[0]]["4. close"]),
                }
            return {"error": data.get("Note", "获取失败"), "symbol": symbol}
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def get_fx_rate(self, from_currency: str = "USD", to_currency: str = "CNY") -> Dict:
        """获取汇率"""
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency,
            "to_currency": to_currency,
            "apikey": self.api_key
        }
        try:
            resp = requests.get(ALPHA_VANTAGE_BASE, params=params, timeout=10)
            data = resp.json()
            if "Realtime Currency Exchange Rate" in data:
                r = data["Realtime Currency Exchange Rate"]
                return {
                    "from": r.get("1. From_Currency Code", ""),
                    "to": r.get("3. To_Currency Code", ""),
                    "rate": float(r.get("5. Exchange Rate", 0)),
                }
            return {"error": data.get("Note", "获取失败")}
        except Exception as e:
            return {"error": str(e)}

    def get_crypto_daily(self, symbol: str = "BTC", market: str = "USD") -> Dict:
        """获取加密货币每日数据"""
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": symbol,
            "market": market,
            "apikey": self.api_key
        }
        try:
            resp = requests.get(ALPHA_VANTAGE_BASE, params=params, timeout=10)
            data = resp.json()
            if "Time Series (Digital Currency Daily)" in data:
                ts = data["Time Series (Digital Currency Daily)"]
                dates = sorted(ts.keys(), reverse=True)[:5]
                latest = ts[dates[0]]
                return {
                    "symbol": symbol,
                    "market": market,
                    "latest_date": dates[0],
                    "close_price": latest.get("4b. close (USD)", 0),
                }
            return {"error": data.get("Note", "获取失败"), "symbol": symbol}
        except Exception as e:
            return {"error": str(e), "symbol": symbol}


if __name__ == "__main__":
    tool = AlphaVantageTool()

    print("=== 测试 get_quote (IBM) ===")
    print(tool.get_quote("IBM"))

    print("\n=== 测试 get_fx_rate (USD->CNY) ===")
    print(tool.get_fx_rate("USD", "CNY"))
