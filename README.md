# 🤖 Multi-Agent Task Orchestrator

An intelligent AI-powered task orchestration system that uses multiple specialized agents to collaboratively plan, execute, and review complex tasks. Built with LangGraph, FastAPI, and React.

Multi-Agent Orchestrator
FastAPI
React
MongoDB

## ✨ Features

### 🎯 Multi-Agent Orchestration
- **Planner Agent**: Creates step-by-step execution plans
- **Executor Agent**: Performs tasks based on the plan
- **Critic Agent**: Reviews and validates outputs
- **Supervisor Agent**: Orchestrates the entire workflow

### 🔐 Authentication & Security
- **Dual Authentication**: Username/password and Google OAuth
- **JWT Token Management**: Secure 24-hour sessions
- **User Isolation**: Each user's data is completely separate
- **Password Security**: Bcrypt hashing with strength validation

### 💬 Chat Interface
- **Real-time Conversations**: Seamless interaction with AI agents
- **Session Management**: Save and resume conversations
- **Chat History**: Access all previous conversations
- **Beautiful UI**: Modern dark theme with smooth animations

### 🗄️ Data Persistence
- **MongoDB Integration**: All conversations stored securely
- **User Profiles**: Track user activity and preferences
- **Session Filtering**: Users see only their own sessions

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI Orchestration**: LangGraph
- **LLM Providers**: OpenAI, Groq, Google Gemini
- **Database**: MongoDB (Motor async driver)
- **Authentication**: JWT, OAuth 2.0
- **Security**: Bcrypt, python-jose

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **State Management**: Context API
- **UI/UX**: Custom components, smooth animations

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB 6.0+
- OpenAI/Groq/Gemini API Key

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/nivas2823/multi-agent-orchestrator.git
cd multi-agent-orchestrator
```

2. **Install Python dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
```env
# LLM Configuration
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=multi_agent_system

# JWT Authentication
JWT_SECRET_KEY=your_secret_key_here

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
FRONTEND_URL=http://localhost:5173
```


 **Run the backend**

uvicorn app.main:app --reload


Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies**

cd frontend
npm install


2. **Start development server**

npm run dev


Frontend will be available at `http://localhost:5173`

## 📚 API Documentation

Once the backend is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

