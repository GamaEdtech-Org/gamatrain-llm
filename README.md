# Gamatrain AI Research 🤖

Fine-tuning a Large Language Model (Qwen2-1.5B) with Gamatrain's educational content to create an intelligent tutor assistant.

## 🎯 Project Goal

Create an AI assistant that can:
- Answer questions about Gamatrain's educational content (courses, tests, blogs)
- Maintain general intelligence (math, logic, reasoning)
- Be deployed locally using Ollama

## 📊 Results

| Metric | Value |
|--------|-------|
| Base Model | Qwen2-1.5B-Instruct |
| Final Dataset | 2,614 samples |
| Domain Data | 2,422 (Gamatrain blogs, tests, courses) |
| General Data | 192 (math, logic, chat - weighted 4x) |
| Output Format | GGUF (4-bit quantized) |

## 🗂️ Repository Structure

```
gamatrain-ai-research/
├── README.md                 # This file
├── data/
│   ├── gamatrain_final_dataset.jsonl  # Final training dataset
│   ├── gamatrain_finetune_data.jsonl  # Raw Gamatrain data
│   ├── general_knowledge.jsonl        # General knowledge samples
│   └── scripts/
│       ├── extract_and_format_data.py # API data extraction
│       ├── extract_blog_data.py       # Blog sitemap extraction
│       ├── generate_general_data.py   # General knowledge generator
│       ├── create_final_dataset.py    # Dataset merger
│       └── requirements.txt
├── model/
│   ├── Modelfile              # Ollama model configuration
│   └── README.md              # Model download instructions
├── api/
│   ├── llm_server.py          # FastAPI server
│   └── requirements.txt
├── notebooks/
│   └── fine-tuning-demo.ipynb # Google Colab training notebook
└── docs/
    ├── RESEARCH.md            # Research findings
    ├── TRAINING.md            # Training guide
    └── DEPLOYMENT.md          # Deployment guide
```

## 🚀 Quick Start

### 1. Download the Model
See [model/README.md](model/README.md) for download instructions.

### 2. Import to Ollama
```bash
cd model/
ollama create gamatrain-qwen -f Modelfile
```

### 3. Test the Model
```bash
ollama run gamatrain-qwen "What is 2 + 2?"
ollama run gamatrain-qwen "Tell me about Ohm's Law"
ollama run gamatrain-qwen "Does Gamatrain have past papers for Biology?"
```

### 4. Run the API Server (Optional)
```bash
cd api/
pip install -r requirements.txt
python llm_server.py
```

## 📚 Documentation

- **[RESEARCH.md](docs/RESEARCH.md)** - Problem statement, approach, and findings
- **[TRAINING.md](docs/TRAINING.md)** - How to fine-tune the model
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - How to deploy with Ollama

## ⚠️ Key Learning: Catastrophic Forgetting

During development, we discovered that fine-tuning only on domain-specific data caused the model to "forget" basic abilities (like math). The solution was to mix domain data with general knowledge samples.

**Before fix:** `2 + 2 = 0` ❌
**After fix:** `2 + 2 = 4` ✅

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please read the documentation first.
