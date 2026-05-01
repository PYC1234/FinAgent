# FinAgent

基于 LLM 的多资产金融分析 Agent，采用 ReAct 架构。

## 特性

- **LLM 驱动**：使用 SiliconFlow API（DeepSeek）进行智能推理
- **多数据源**：支持加密货币（Binance）、美股（Twelve Data）、外汇（Frankfurter）
- **ReAct 框架**：Thought → Action → Observation → Final Answer
- **RAG 增强**：基于 ChromaDB + sentence-transformers 的向量检索
- **多轮对话**：支持上下文记忆
- **对比分析**：支持多资产对比

## 安装

```bash
# 克隆仓库
git clone https://github.com/PYC1234/FinAgent.git
cd FinAgent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

## 配置

在项目根目录创建 `config.json`：

```json
{
  "llm_provider": "siliconflow",
  "llm": {
    "api_key": "your-api-key",
    "base_url": "https://api.siliconflow.cn/v1",
    "model": "deepseek-ai/DeepSeek-V3",
    "supports_function_calling": true
  },
  "twelve_data_api_key": "your-twelve-data-key"
}
```

- API Key 获取：[SiliconFlow](https://account.siliconflow.cn)
- Twelve Data Key：[Twelve Data](https://twelvedata.com/account/api-keys)（可选）

## 使用

```bash
python main.py
```

### 交互模式

```
你: BTC现在价格多少？
你: 苹果最近走势怎么样？
你: 比较一下ETH和特斯拉的走势
```

## 项目结构

```
finagent/
├── agent/              # Agent 核心
│   └── agent.py        # LLM 驱动的 ReAct Agent
├── tools/             # 工具模块
│   ├── crypto_tool.py  # Binance 加密货币
│   ├── twelve_data_tool.py  # Twelve Data 美股
│   ├── frankfurter_tool.py  # Frankfurter 外汇
│   └── analysis_tool.py    # 金融分析工具
├── rag/                # RAG 模块
│   ├── knowledge.txt   # 金融知识库（源数据）
│   ├── vector_store.py # 向量数据库（ChromaDB）
│   ├── retriever.py    # 检索器（优先向量，降级关键词）
│   └── vector_db/      # ChromaDB 自动生成（无需手动修改）
├── prompts/            # Prompt 模板
├── config.py           # 配置加载器
├── llm_client.py       # LLM API 客户端
└── main.py             # 入口程序
```

## 支持的数据

| 类型 | 数据源 | 示例 |
|------|--------|------|
| 加密货币 | Binance | BTCUSDT, ETHUSDT, SOLUSDT |
| 美股 | Twelve Data | AAPL, TSLA, MSFT |
| 外汇 | Frankfurter | USD, EUR, CNY, JPY |

## RAG 知识检索

FinAgent 使用 RAG (Retrieval-Augmented Generation) 增强 LLM 回答专业性：

```
用户问题 → 向量检索 → 知识库 → LLM 基于知识回答
```

### 工作原理

1. **知识库**：`knowledge.txt` 包含金融概念、公式、指标定义
2. **向量化**：使用 `sentence-transformers` 将文本转为 768 维向量
3. **存储**：ChromaDB 持久化存储向量索引
4. **检索**：语义相似度搜索，返回 top_k 相关知识片段
5. **生成**：LLM 基于检索结果给出专业回答

### 初始化 RAG

```bash
# 首次运行需要初始化向量数据库
python -m rag.vector_store
```

### 配置 HuggingFace 镜像（国内用户）

```bash
# 已在 vector_store.py 中自动设置
# 如果下载失败，手动设置：
set HF_ENDPOINT=https://hf-mirror.com
```

## 分析指标

- 年化收益率
- 波动率（标准差）
- 最大回撤
- 夏普比率
- 对比分析

## 环境要求

- Python 3.8+
- pandas
- requests

## 许可证

MIT
