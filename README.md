# FinAgent

基于 LLM 的多资产金融分析 Agent，采用 ReAct 架构。

## 特性

- **LLM 驱动**：使用 SiliconFlow API（DeepSeek）进行智能推理
- **多数据源**：支持加密货币（Binance）、美股（Twelve Data）、外汇（Frankfurter）
- **ReAct 框架**：Thought → Action → Observation → Final Answer
- **RAG 增强**：内置金融知识检索
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
│   ├── knowledge.txt   # 金融知识库
│   └── retriever.py    # 知识检索
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
