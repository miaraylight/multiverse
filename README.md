# 🧠 Multiverse Chat Interface

## Overview

**Multiverse** is a unified chat platform that lets users interact with multiple AI models (e.g., GPT, Claude, Gemini, LLaMA, etc.) in a single conversation thread. It’s designed for comparison, collaboration, and exploration of different language models in real-time.

## ✨ Features

- 🔁 Switch between AI models seamlessly within a single conversation
- 💬 Compare responses from different models side-by-side
- 🧩 Plug-and-play support for multiple model APIs
- 🗂️ Save, export, and review conversations
- 🌐 Web-based UI with responsive design
- 🔒 Authentication and API key management

## 🚀 Getting Started

### Prerequisites

- Node.js `>= 18`
- Python `>= 3.8` (if using self-hosted models)
- API keys for supported AI services (e.g., OpenAI, Anthropic, Google, etc.)

### Installation

```bash
git clone https://github.com/miaraylight/multiverse
cd client
npm install
```

### Configuration

Create a `.env` file and add your API keys:

```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_claude_key
GOOGLE_API_KEY=your_gemini_key
```

### Run the App

```bash
npm run dev
```

Visit `http://localhost:3000` in your browser.

## 🔌 Supported Models

- **OpenAI GPT-4 / GPT-3.5**
- **Anthropic Claude 2 / 3**
- **Google Gemini Pro**
- **Meta LLaMA (via local or cloud-hosted API)**
- **Custom / Open Source LLMs (via REST API)**

## 📐 Architecture

- **Frontend:** React + TailwindCSS
- **Backend:** Node.js + Express or Python FastAPI (configurable)
- **Model Adapters:** Modular system to support different APIs

## 📦 API Routes

| Route            | Description                   |
|------------------|-------------------------------|
| `/api/chat`      | Unified chat endpoint         |
| `/api/models`    | Get list of available models  |
   |   |

## 🤖 Usage Example

```bash
User: "Explain quantum physics"
→ GPT-4: [response]
→ Claude 3: [response]
→ Gemini: [response]
```

You can switch models mid-conversation by clicking or typing a command like `/use claude`.

## 🛠️ Roadmap

- [ ] Per-message model tagging
- [ ] History sync across sessions
- [ ] Voice input and TTS output
- [ ] Self-hosted model integration (e.g., Ollama, LM Studio)

## 🤝 Contributing

Pull requests are welcome! Please fork the repo and submit your changes via a PR.