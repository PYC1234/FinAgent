"""
RAG检索器 - 支持向量检索（带关键词匹配降级）
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

        # 尝试加载向量数据库
        self.vector_store = None
        self._init_vector_store()

    def _init_vector_store(self):
        """初始化向量数据库"""
        try:
            from rag.vector_store import VectorStore, load_knowledge_chunks
            self.vector_store = VectorStore()
            chunks = load_knowledge_chunks()
            if chunks:
                self.vector_store.clear()
                self.vector_store.add_texts(chunks)
                print(f"[Retriever] 向量数据库已就绪，包含 {len(chunks)} 个知识片段")
        except ImportError as e:
            print(f"[Retriever] 向量数据库未安装，使用关键词匹配: {e}")
        except Exception as e:
            print(f"[Retriever] 向量数据库初始化失败，使用关键词匹配: {e}")

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
        优先使用向量检索，降级到关键词匹配
        """
        # 优先向量检索
        if self.vector_store is not None:
            try:
                results = self.vector_store.search(query, top_k=top_k)
                if results:
                    return "\n\n".join(results)
            except Exception as e:
                print(f"[Retriever] 向量检索失败，降级到关键词: {e}")

        # 降级：关键词匹配
        return self._keyword_match(query, top_k)

    def _keyword_match(self, query: str, top_k: int = 3) -> str:
        """基于关键词匹配检索（降级方案）"""
        if not self.knowledge_base:
            return ""

        query_lower = query.lower()
        lines = self.knowledge_base.split("\n")

        keywords_map = {
            "收益率": ["收益率", "return", "收益", "年化", "日收益率"],
            "波动率": ["波动率", "volatility", "波动", "风险", "标准差"],
            "回撤": ["回撤", "drawdown", "最大回撤", "亏损"],
            "夏普": ["夏普", "sharpe", "风险调整"],
            "比较": ["比较", "对比", "compare", "资产对比"],
            "技术指标": ["技术指标", "MA", "MACD", "RSI", "移动平均", "金叉", "死叉"],
            "数据处理": ["数据", "处理", "缺失", "异常", "填充"],
        }

        relevant_sections = []
        current_section = []
        current_keywords = set()

        for line in lines:
            if line.startswith("#"):
                if current_section and current_keywords:
                    relevant_sections.append(("\n".join(current_section), len(current_keywords)))
                current_section = [line]
                current_keywords = set()
                section_title = line.lower()
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

        relevant_sections.sort(key=lambda x: x[1], reverse=True)

        results = []
        for section, score in relevant_sections[:top_k]:
            if score > 0:
                results.append(section)

        if results:
            return "\n\n".join(results)
        return self.knowledge_base[:500]

    def add_knowledge(self, text: str):
        """追加知识到向量库"""
        if self.vector_store is not None:
            self.vector_store.add_texts([text])
        self.knowledge_base += "\n" + text


if __name__ == "__main__":
    retriever = Retriever()

    print("\n" + "=" * 60)
    print("测试检索:")
    print("=" * 60)

    test_queries = [
        "夏普比率是什么",
        "如何计算波动率",
        "MACD指标怎么用",
        "最大回撤什么意思",
        "RSI超买超卖怎么看"
    ]

    for q in test_queries:
        print(f"\n查询: {q}")
        print("-" * 40)
        result = retriever.retrieve(q)
        print(result[:200] if len(result) > 200 else result)
