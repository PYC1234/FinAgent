# FinAgent

Multi-asset financial analysis Agent powered by LLM (ReAct framework).

## Features

- **LLM-powered**: Uses SiliconFlow API (Qwen) for intelligent reasoning
- **Multi-source data**: Supports Crypto (Binance) and A-shares (baostock)
- **ReAct framework**: Thought → Action → Observation → Final Answer
- **RAG enhancement**: Built-in financial knowledge retrieval
- **Comparative analysis**: Compare crypto vs stocks performance

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/finagent.git
cd finagent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create `config.json` in the project root:

```json
{
  "siliconflow": {
    "api_key": "your-api-key",
    "model": "Qwen/Qwen2.5-7B-Instruct"
  }
}
```

Get your API key from [SiliconFlow](https://account.siliconflow.cn).

## Usage

```bash
python main.py
```

### Demo Mode
Run preset example questions automatically.

### Interactive Mode
Ask your own financial analysis questions:

```
你: BTC现在价格多少？
你: 招商银行最近走势怎么样？
你: BTC和茅台对比分析
```

## Project Structure

```
finagent/
├── agent/              # Agent core
│   ├── agent.py       # LLM-driven ReAct Agent
│   └── router.py      # Data source router
├── tools/             # Tool modules
│   ├── crypto_tool.py # Binance API
│   ├── stock_tool.py  # baostock A-share
│   └── analysis_tool.py # Financial analysis
├── rag/               # RAG modules
│   ├── knowledge.txt  # Financial knowledge base
│   └── retriever.py   # Knowledge retrieval
├── prompts/           # Prompt templates
├── config.py          # Configuration loader
├── llm_client.py     # SiliconFlow API client
└── main.py           # Entry point
```

## Supported Data

| Type | Source | Examples |
|------|--------|----------|
| Crypto | Binance | BTCUSDT, ETHUSDT, SOLUSDT |
| A-Share | baostock | sh.600036, sh.600519, sz.000001 |

## Analysis Metrics

- Annualized return
- Volatility (standard deviation)
- Max drawdown
- Sharpe ratio
- Comparative analysis

## Requirements

- Python 3.8+
- pandas
- requests
- baostock

## License

MIT
