# 🧳 Cross-Border Travel Assistant

This project uses **LangGraph** to create an AI assistant that helps users understand travel documentation when moving between two countries. The assistant provides guidance on:

1. 🛂 **Visa Requirements**  
2. 🪪 **Passport Requirements**  
3. ⚠️ **Travel Advisories**  
4. 📄 **Additional Documents**

---

## 🚀 Getting Started

### 📦 Clone the Repository

```bash
git clone https://github.com/your-username/cross-border-travel-assistant.git
cd cross-border-travel-assistant
```

### ⚡ Install `uv` (if you don't have it)

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

or via Homebrew:

```bash
brew install astral-sh/uv/uv
```

---

### 🛠️ Setup the Environment

1. **Create a virtual environment**

```bash
uv venv
```

2. **Activate it**

- On macOS/Linux:

  ```bash
  source .venv/bin/activate
  ```

- On Windows:

  ```cmd
  .venv\Scripts\activate
  ```

3. **Install dependencies**

```bash
uv sync
```

---

### 🔐 Environment Variables

1. Create a `.env` file:

```bash
cp .env.example .env
```

2. Open `.env` and fill in the required API keys and secrets (e.g., OpenAI, etc.)

---

### ▶️ Run the App

```bash
langgraph dev
```

---

## 📚 Stack

- **LangGraph** – for building stateful multi-step LLM applications
- **uv** – for fast dependency management
- **Python 3.11+**

---

## 🧠 Assistant Role

The assistant is designed to:

> Help users understand the following documents when traveling between two countries:
> 1. Visa Requirements  
> 2. Passport Requirements  
> 3. Travel Advisories  
> 4. Additional Documents

---

## 🙌 Contributing

Contributions, issues, and PRs are welcome!

---

## 📄 License

[MIT License](LICENSE)
