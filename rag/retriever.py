"""
RAG检索器 - 简单知识匹配
"""
import os
from typing import List, Dict


class Retriever:
    """从知识库中检索相关内容"""

    def __init__(self, knowledge_path: str = None):
        if knowledge_path is None:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            knowledge_path = os.path.join(base, "rag", "knowledge.txt")
        self.knowledge_path = knowledge_path
        self.knowledge_base = self._load_knowledge()

    def _load_knowledge(self) -> str:
        """加载知识库"""
        try:
            with open(self.knowledge_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""

    def retrieve(self, query: str, top_k: int = 3) -> str:
        """
        根据query检索相关知识
        简单实现：基于关键词匹配
        """
        if not self.knowledge_base:
            return ""

        query_lower = query.lower()
        lines = self.knowledge_base.split("\n")

        # 关键词映射
        keywords_map = {
            "收益率": ["收益率", "return", "收益"],
            "波动率": ["波动率", "volatility", "波动", "风险"],
            "回撤": ["回撤", "drawdown", "最大回撤"],
            "夏普": ["夏普", "sharpe", "风险调整"],
            "比较": ["比较", "对比", "compare"],
            "技术指标": ["技术指标", "MA", "MACD", "RSI", "移动平均"],
            "数据": ["数据", "处理", "缺失", "异常"],
        }

        # 查找相关章节
        relevant_sections = []
        current_section = []
        current_keywords = set()

        for line in lines:
            if line.startswith("## "):
                if current_section and current_keywords:
                    relevant_sections.append(("\n".join(current_section), len(current_keywords)))
                current_section = [line]
                section_title = line.lower()
                current_keywords = set()
                for key, kws in keywords_map.items():
                    if any(kw in section_title for kw in kws) or any(kw in query_lower for kw in kws):
                        current_keywords.add(key)
            elif line.strip() and current_section:
                current_section.append(line)
                line_lower = line.lower()
                for key, kws in keywords_map.items():
                    if any(kw in line_lower and kw in query_lower for kw in kws):
                        current_keywords.add(key)

        if current_section and current_keywords:
            relevant_sections.append(("\n".join(current_section), len(current_keywords)))

        # 按相关性排序
        relevant_sections.sort(key=lambda x: x[1], reverse=True)

        # 返回top_k个结果
        results = []
        for section, score in relevant_sections[:top_k]:
            if score > 0:
                results.append(section)

        if results:
            return "\n\n".join(results)
        return self.knowledge_base[:500]  # 返回开头部分作为默认

    def add_knowledge(self, text: str):
        """追加知识"""
        self.knowledge_base += "\n" + text


if __name__ == "__main__":
    retriever = Retriever()
    print(retriever.retrieve("如何计算波动率"))
    print("\n" + "=" * 50 + "\n")
    print(retriever.retrieve("比较股票和加密货币"))
