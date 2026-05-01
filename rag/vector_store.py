"""
向量数据库 - 基于 ChromaDB
"""
import os
from typing import List, Optional

import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

try:
    from chromadb import Client
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class VectorStore:
    """向量存储和检索"""

    def __init__(self, persist_dir: str = None):
        if not CHROMADB_AVAILABLE:
            raise ImportError("请先安装依赖: pip install chromadb sentence-transformers")

        if persist_dir is None:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            persist_dir = os.path.join(base, "rag", "vector_db")

        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        settings = Settings(
            chroma_api_impl='chromadb.api.rust.RustBindingsAPI',
            is_persistent=True,
            persist_directory=persist_dir
        )
        self.client = Client(settings=settings)
        self.collection = self.client.get_or_create_collection("financial_knowledge")

        # 支持中英文的embedding模型
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def add_texts(self, texts: List[str], ids: List[str] = None):
        """添加文本到向量库"""
        if ids is None:
            ids = [str(i) for i in range(len(texts))]

        embeddings = self.model.encode(texts).tolist()

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts
        )

    def search(self, query: str, top_k: int = 3) -> List[str]:
        """语义检索"""
        query_emb = self.model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_emb,
            n_results=top_k
        )
        return results["documents"][0] if results["documents"] else []

    def clear(self):
        """清空向量库"""
        self.client.delete_collection("financial_knowledge")
        self.collection = self.client.get_or_create_collection("financial_knowledge")


def load_knowledge_chunks() -> List[str]:
    """从 knowledge.txt 加载并切分成段落"""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    knowledge_path = os.path.join(base, "rag", "knowledge.txt")

    chunks = []
    current_chunk = []

    with open(knowledge_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                if current_chunk:
                    chunk_text = " ".join(current_chunk)
                    if chunk_text:
                        chunks.append(chunk_text)
                    current_chunk = []
            else:
                current_chunk.append(line)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return [c for c in chunks if len(c) > 10]


if __name__ == "__main__":
    print("初始化向量数据库...")

    store = VectorStore()
    chunks = load_knowledge_chunks()

    print(f"加载 {len(chunks)} 个知识段落")
    store.add_texts(chunks)
    print("向量数据库创建成功！")

    print("\n测试检索:")
    results = store.search("夏普比率是什么")
    for i, r in enumerate(results, 1):
        print(f"\n结果 {i}: {r[:100]}...")
