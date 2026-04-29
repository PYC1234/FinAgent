"""
Crypto数据获取工具 - Binance API
"""
import requests
import pandas as pd
from typing import Dict, List, Optional


class CryptoTool:
    """获取加密货币实时/历史数据"""

    BASE_URL = "https://api.binance.com/api/v3"

    def __init__(self):
        self.name = "crypto_tool"
        self.description = "获取加密货币价格数据，支持BTC、ETH等主流币种"

    def get_symbols(self) -> List[str]:
        """获取支持的交易对"""
        return ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT"]

    def get_price(self, symbol: str = "BTCUSDT") -> Dict:
        """获取单个币种当前价格"""
        url = f"{self.BASE_URL}/ticker/price"
        params = {"symbol": symbol.upper()}
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return {
                "symbol": data["symbol"],
                "price": float(data["price"]),
            }
        except Exception as e:
            return {"error": str(e)}

    def get_prices(self, symbols: Optional[List[str]] = None) -> List[Dict]:
        """批量获取币种价格"""
        if symbols is None:
            symbols = self.get_symbols()
        return [self.get_price(s) for s in symbols]

    def get_klines(self, symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 100) -> pd.DataFrame:
        """获取K线数据（OHLCV）"""
        url = f"{self.BASE_URL}/klines"
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            df = pd.DataFrame(data, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_volume", "trades", "taker_buy_base",
                "taker_buy_quote", "ignore"
            ])
            df["open"] = df["open"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)
            df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
            return df[["open_time", "open", "high", "low", "close", "volume"]]
        except Exception as e:
            return pd.DataFrame()

    def get_24h_stats(self, symbol: str = "BTCUSDT") -> Dict:
        """获取24小时统计信息"""
        url = f"{self.BASE_URL}/ticker/24hr"
        params = {"symbol": symbol.upper()}
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return {
                "symbol": data["symbol"],
                "price_change": float(data["priceChange"]),
                "price_change_pct": float(data["priceChangePercent"]),
                "high": float(data["highPrice"]),
                "low": float(data["lowPrice"]),
                "volume": float(data["volume"]),
                "quote_volume": float(data["quoteVolume"]),
            }
        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    tool = CryptoTool()
    print("BTC价格:", tool.get_price("BTCUSDT"))
    print("\n24h统计:", tool.get_24h_stats("BTCUSDT"))
    print("\nK线数据:", tool.get_klines("BTCUSDT", limit=5).to_dict())
