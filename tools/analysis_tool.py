"""
金融分析工具 - 统计计算
"""
import pandas as pd
import numpy as np
from typing import Dict, List


class AnalysisTool:
    """金融指标计算工具"""

    def __init__(self):
        self.name = "analysis_tool"
        self.description = "计算金融分析指标：均值、波动率、收益率等"

    def calculate_returns(self, prices: pd.Series) -> pd.Series:
        """计算收益率序列"""
        return prices.pct_change().dropna()

    def mean_return(self, prices: pd.Series, annualize: bool = True) -> float:
        """计算平均收益率"""
        returns = self.calculate_returns(prices)
        mean = returns.mean()
        if annualize and len(returns) > 0:
            return mean * 252  # 年化
        return mean

    def volatility(self, prices: pd.Series, annualize: bool = True) -> float:
        """计算波动率（标准差）"""
        returns = self.calculate_returns(prices)
        vol = returns.std()
        if annualize and len(returns) > 0:
            return vol * np.sqrt(252)  # 年化
        return vol

    def max_drawdown(self, prices: pd.Series) -> float:
        """计算最大回撤"""
        cumulative = (1 + self.calculate_returns(prices)).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()

    def sharpe_ratio(self, prices: pd.Series, risk_free_rate: float = 0.03) -> float:
        """计算夏普比率"""
        returns = self.calculate_returns(prices)
        if returns.std() == 0:
            return 0.0
        mean_ret = returns.mean() * 252
        vol = returns.std() * np.sqrt(252)
        return (mean_ret - risk_free_rate) / vol

    def summary(self, prices: pd.Series, name: str = "Asset") -> Dict:
        """生成分析摘要"""
        returns = self.calculate_returns(prices)
        return {
            "asset": name,
            "latest_price": prices.iloc[-1] if len(prices) > 0 else 0,
            "mean_return_annual": self.mean_return(prices),
            "volatility_annual": self.volatility(prices),
            "max_drawdown": self.max_drawdown(prices),
            "sharpe_ratio": self.sharpe_ratio(prices),
            "data_points": len(prices),
        }

    def compare_assets(self, price_dict: Dict[str, pd.Series]) -> pd.DataFrame:
        """对比多个资产"""
        records = []
        for name, prices in price_dict.items():
            s = self.summary(prices, name)
            records.append(s)
        return pd.DataFrame(records)


if __name__ == "__main__":
    # 测试
    tool = AnalysisTool()
    prices = pd.Series([100, 105, 102, 108, 107, 110, 115, 112])
    print("收益率:", tool.calculate_returns(prices).values)
    print("年化收益:", tool.mean_return(prices))
    print("年化波动率:", tool.volatility(prices))
    print("最大回撤:", tool.max_drawdown(prices))
    print("夏普比率:", tool.sharpe_ratio(prices))
    print("摘要:", tool.summary(prices, "TEST"))
