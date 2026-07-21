<div align="center">
  <img src="https://via.placeholder.com/150x150.png?text=BugMind+AI" alt="BugMind AI Logo" width="150" />
  
  # BugMind AI 🧠
  **The Ultimate AI-Powered Code Analysis Platform & Web IDE**

  [![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)](https://nextjs.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
  [![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python)](https://python.org/)
  [![MongoDB](https://img.shields.io/badge/MongoDB-Async-47A248?logo=mongodb)](https://mongodb.com/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

  [Live Demo (Vercel)](#) • [Report Bug](#) • [Request Feature](#)
</div>

---

## 🌟 About BugMind AI

BugMind AI is an intelligent, full-stack codebase analysis platform and web-based IDE designed to help developers identify, triage, and fix bugs instantly. 

By combining traditional static analysis tools with cutting-edge Large Language Models (LLMs), BugMind AI understands context deeply, identifies runtime & logical issues, and provides actionable, context-aware suggestions directly within the browser. 

---

## 🚀 Key Features & Capabilities

### 1. 💻 Interactive Web IDE
- **Monaco Editor Integration**: A robust built-in code editor powered by the same engine as VS Code.
- **Secure Code Execution Sandbox**: Write and execute code directly in your browser. Get instant terminal output and tracebacks for languages like Python, JavaScript, Go, and more.
- **Multi-language Support**: Fully supports syntax highlighting and execution for Python, JavaScript, TypeScript, Go, Java, C++, C, Rust, Ruby, and PHP.

### 2. 🤖 Real-time AI Code Review & Auto-Fix
- **Deep Bug Detection**: Detects syntax errors, logical bugs, and performance bottlenecks instantly.
- **Step-by-Step Explanations**: The AI breaks down the bug, explains *why* it happens, and teaches you how to fix it.
- **Corrected Code Generation**: Automatically provides a fully corrected version of your code in a beautiful UI.
- **Free API Support (Groq/OpenRouter)**: Fully configurable `OPENAI_BASE_URL` allows you to bypass paid OpenAI limits and use extremely fast, free alternatives like **Groq (Llama 3)**.

### 3. 🛡️ Advanced Security & Static Analysis
- **Static Analysis Engine**: Runs traditional static analysis tools (`Semgrep`, `Bandit`, `Pylint`) for deep security and code quality checks before sending code to the AI.
- **Robust Error Handling**: If your API keys expire or fail, BugMind AI gracefully catches the error and provides detailed UI feedback to help you troubleshoot API issues.

### 4. 🧠 Context-Aware RAG (Retrieval-Augmented Generation)
- **ChromaDB Vector Store**: Ingests entire repositories, allowing the AI to understand the full context of your codebase rather than just single files.
- **Interactive AI Chat**: Ask codebase-specific questions and get answers referencing your actual project files.

### 5. 🔒 Enterprise-Grade Architecture
- **Async MongoDB**: High-performance asynchronous database operations using `Motor`.
- **JWT Authentication**: Secure user registration, login, and session management.

---

## 🔄 Recent Activities & Updates

- **[NEW] Free AI Integration**: Added configuration for `OPENAI_BASE_URL` to support free APIs like Groq, so developers can use BugMind without paying for OpenAI credits.
- **[NEW] "Corrected Code" UI**: Built a sleek frontend component to extract and display the AI's corrected code in a dedicated, syntax-highlighted box.
- **[NEW] Smart Fallback System**: Added robust API error catching. If the OpenAI API fails (e.g., rate limits, invalid keys), the UI now explicitly reports the exact error to the developer instead of failing silently.
- **[NEW] Sandbox Execution Engine**: Added support for creating temporary directories and executing raw code snippets, piping `stdout` and `stderr` directly back to the Web IDE terminal.

---

## 🛠️ Technology Stack

| Category | Technologies |
|----------|--------------|
| **Frontend** | Next.js (App Router), React, TailwindCSS, Framer Motion, Monaco Editor, React Markdown |
| **Backend API** | Python, FastAPI, Uvicorn, Pydantic |
| **Database** | MongoDB (Async Motor) |
| **AI / NLP** | OpenAI Python SDK, Groq (via Base URL), LangChain, ChromaDB |
| **Security** | JWT (JSON Web Tokens), bcrypt |
| **Execution** | Subprocess Sandbox (`/tmp/` isolation) |
| **Deployment** | Vercel (Frontend), Render (Backend), Docker Compose |

---

## ⚙️ Getting Started & Installation

### Option 1: Quick Start (Windows Local)
We have provided a convenient batch script to start both the frontend and backend simultaneously on your local machine.

```cmd
git clone https://github.com/VinayKumarMakvana/bugmind-ai.git
cd bugmind-ai
.\start.bat
```
*(This script will automatically install NPM packages, create a Python virtual environment, install requirements, and start both servers).*

### Option 2: Live Deployment (Vercel + Render)
If you are deploying BugMind AI to production, ensure the following Environment Variables are configured in your backend (e.g., Render Dashboard):

```env
# MongoDB Connection String (e.g., MongoDB Atlas)
DATABASE_URL="mongodb+srv://<user>:<password>@cluster.mongodb.net/..."

# Frontend URL to allow CORS
FRONTEND_URL="https://bugmind-ai.vercel.app"

# Security Key for JWT
SECRET_KEY="your-secure-random-string"

# AI Configuration (OpenAI or Groq)
OPENAI_API_KEY="your-api-key"
OPENAI_MODEL="gpt-3.5-turbo" # Or "llama3-70b-8192" for Groq

# (Optional) Use Groq for Free AI Analysis
OPENAI_BASE_URL="https://api.groq.com/openai/v1"
```

---

## 💡 How to Use BugMind AI

1. **Sign Up / Login**: Create a secure account on the platform.
2. **Open the Web IDE**: Navigate to the Editor page.
3. **Write Code**: Paste your code (Python, JS, etc.) into the Monaco Editor.
4. **Execute**: Click `Run Code` to execute the code in the backend sandbox and see terminal output instantly.
5. **Analyze**: Click `Run Analysis`. The backend will parse your code, run static checks, send it to the LLM (OpenAI/Groq), and return a highly detailed breakdown of bugs, fixes, and the corrected code.

---

<div align="center">
  <i>Built with ❤️ for developers who hate bugs.</i>
</div>
