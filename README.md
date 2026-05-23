# Autonomous Multi-Agent DevOps & Code Critic Engine

An enterprise-grade, closed-loop AI DevOps pipeline that automates code reviews, software test generation, and secure execution validation. Powered by the next-generation Microsoft AutoGen framework, this system runs entirely within isolated Docker sandboxes and deploys natively as a cloud-based CI/CD worker via GitHub Actions.

## 🏗️ System Architecture

When a developer opens a Pull Request, the system orchestrates an asynchronous debate between specialized AI models to write, test, and validate changes before deployment.

```text
[ Developer Opens PR ]
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ GitHub Actions Runner (CI/CD Production Environment)  │
│  - Pulls Code Changes (.diff)                          │
│  - Sets Environment Variables & API Secrets            │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│   Microsoft AutoGen Orchestration Loop                 │
│                                                        │
│  ┌──────────────────┐         ┌────────────────────┐   │
│  │                  ├────────►│                    │   │
│  │ Software Engineer│         │    Code Critic     │   │
│  │     (Coder)      │◄────────┤    (QA/Security)   │   │
│  └──────────────────┘         └─────────┬──────────┘   │
└─────────────────────────────────────────┼──────────────┘
                                          │
                     Invokes Safe Tool    │
                     With Generated Code  ▼
┌────────────────────────────────────────────────────────┐
│      Isolated Docker Container Sandbox Environment    │
│  - Installs runtime dependencies                       │
│  - Executes untrusted AI code via 'pytest'             │
│  - Captures runtime errors & prevents memory leaks     │
└─────────────────────────┬──────────────────────────────┘
                          │ Sends Execution Logs
                          ▼
             [ Loop Repeats Until APPROVED ]
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│   Automated Downstream Actions                         │
│  - Compiles full conversational transcript             │
│  - Logs system execution token usage                   │
│  - Posts Markdown review summary back to GitHub PR     │
└────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack & Core AI Concepts

*   **Multi-Agent Orchestration:** Built with `autogen-agentchat` and `autogen-ext` to enforce structured group communication, custom termination behaviors, and programmatic flow controls.
*   **LLM Integration Layer:** Powered by `litellm` and `OpenAIChatCompletionClient` for smooth, vendor-agnostic swapping between OpenAI, Azure OpenAI, and localized open-source models (Ollama/Llama-3).
*   **Production MLOps Sandbox:** Utilizes **Docker** to safely build and isolate runtime processes, eliminating targets for code injection and protecting the host machine from infinite code loops.
*   **Automated Deployment:** Written in **Asynchronous Python (`asyncio`)** and bundled into **GitHub Actions CI/CD workflows** for live, real-time repository management.

## 🚀 Step-by-Step Execution Guide

### 1. Local Development Setup (Using Cursor)
Ensure Docker Desktop is open and running on your local machine.

```bash
# Clone your repository and navigate into the folder
cd agentic-devops-engine

# Initialize a virtual environment and activate it
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install the production dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a local file named `.env` in the root directory to store your credentials:
```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 3. Local Run & Verification
Execute the central entry point in your Cursor terminal to watch the local multi-agent feedback loop in action:
```bash
python src/main.py
```

### 4. Deploying to Cloud Production (GitHub Actions)
1. Commit and push all your files to the `main` branch of your remote GitHub repository.
2. Open your GitHub Repository on the web web browser and navigate to **Settings** -> **Secrets and variables** -> **Actions**.
3. Create a **New repository secret** named `OPENAI_API_KEY` and paste your actual platform access token.
4. Open a test branch, add changes to a file, and submit a **Pull Request**. The live production worker will wake up and handle your review automatically.

## 📊 Resume Bullet Points (Copy & Paste for Your CV)

*   **AI Software Engineer / DevOps Architect**
    *   Designed and engineered an enterprise-grade, closed-loop **Multi-Agent AI DevOps Engine** using the next-generation **Microsoft AutoGen framework** to automate pull request code reviews and software test generation.
    *   Implemented a secure, production-grade model tool-calling architecture by wrapping untrusted, AI-generated source files inside localized **Docker sandboxes**, preventing remote code executions and handling infinite runtime loops via custom process limits.
    *   Architected a full **asynchronous cloud pipeline using Python (`asyncio`) and GitHub Actions**, enabling AI agents to ingest raw Git modifications, execute code test scripts programmatically, and deliver automated markdown summaries back to active pull request threads.
