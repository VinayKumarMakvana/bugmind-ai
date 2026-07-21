# BugMind AI - AI-Powered Code Analysis & Web IDE

BugMind AI is an intelligent codebase analysis platform and web-based IDE that helps developers identify, triage, and fix bugs instantly. It uses cutting-edge AI models combined with powerful static analysis tools to understand context, identify issues, and provide actionable, context-aware suggestions directly within the browser.

## Features

- 🤖 **Real-time AI Code Review** - Uses advanced OpenAI models to automatically review code, identify issues, and suggest precise corrections.
- 💻 **Monaco Web IDE** - A robust built-in code editor in the browser (powered by the same engine as VS Code) to view and edit code with real-time AI assistance.
- 🔍 **Static Analysis Integration** - Runs traditional static analysis tools (Semgrep, Bandit, Pylint) for deep security and code quality checks.
- 🧠 **Context-Aware RAG (Retrieval-Augmented Generation)** - Utilizes ChromaDB to ingest repositories, allowing the AI to understand the full context of your entire codebase.
- 💬 **AI Chat Assistant** - Interact with a conversational AI that can explain code, answer questions, and provide guidance based on your specific project.
- 🔗 **Repository & Webhook Management** - Connect code repositories and trigger automated analysis via webhooks seamlessly.
- 📊 **Intelligent Dashboard** - View analysis results, code scores, and overall metrics in a sleek, modern UI.
- 🧩 **AST Parsing & Execution** - Deeply parses code structures for semantic understanding and executes precise analysis.
- 🔒 **Secure & Native** - Your code is processed securely with robust JWT authentication and entirely in-memory processing.

## Technology Stack

- **Frontend**: Next.js (App Router), React, TailwindCSS, Framer Motion, Monaco Editor, React Markdown
- **Backend**: Python, FastAPI, Uvicorn, Motor (async MongoDB), Pydantic
- **AI/ML**: OpenAI, LangChain, ChromaDB
- **Static Analysis**: Semgrep, Bandit, Pylint
- **Authentication**: JWT, bcrypt
- **Containerization**: Docker, Docker Compose

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB
- Git

### Installation

#### Option 1: Quick Start (Windows)

We have provided a convenient batch script to start both the frontend and backend simultaneously on Windows.

```cmd
.\start.bat
```
This will open two terminal windows, install necessary dependencies, and start both servers.

#### Option 2: Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd bugmind-ai
```

2. Start the application:
```bash
docker-compose up --build
```

3. Access the application at:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

#### Option 3: Manual Installation

1. **Backend Setup**:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

2. **Frontend Setup**:
```bash
cd frontend
npm install
```

3. **Database Setup**:
   - Ensure MongoDB is running
   - Create a `.env` file in the `backend` directory:
   ```env
   MONGO_URI=mongodb://localhost:27017/bugmind
   JWT_SECRET=your_secret_key
   OPENAI_API_KEY=your_openai_key
   ```

4. **Run the Application**:
   - Start backend:
     ```bash
     cd backend
     python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
     ```
   - Start frontend:
     ```bash
     cd frontend
     npm run dev
     ```

## Usage

### 1. User Authentication
- Register a new account securely.
- Login with your credentials to access the Dashboard and Editor.

### 2. Using the Web IDE
- Navigate to the "Editor" to launch the Web IDE.
- Paste or write your code directly in the browser.
- Get real-time AI code analysis, error detection, and suggested fixes streamed directly to your screen.

### 3. Repository Analysis
- Go to the Dashboard and link your repository or upload code.
- BugMind AI uses its static analysis engine (Semgrep, Bandit, Pylint) and AI models to comprehensively review the code.
- View structured summaries, severity levels, and deep insights.

### 4. Interactive AI Chat
- Use the built-in AI Chat interface to ask codebase-specific questions.
- The ChromaDB-powered RAG system ensures answers are highly relevant to your uploaded projects.

## Project Structure

```
bugmind-ai/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── api/          # API routes (auth, analyze, chat, repos, webhooks)
│   │   ├── services/     # Core logic (AI Reviewer, RAG, Static Analysis)
│   │   ├── models/       # Pydantic & MongoDB models
│   │   └── core/         # Config and Events
│   ├── requirements.txt
│   └── .env
├── frontend/             # Next.js React frontend
│   ├── src/
│   │   ├── app/          # App Router (dashboard, editor, login, settings)
│   │   ├── components/   # Reusable UI components
│   │   └── lib/          # Utilities and configurations
│   ├── package.json
│   └── .env.local
├── start.bat             # Quickstart script for Windows
└── README.md
```

## License

This project is licensed under the MIT License.
