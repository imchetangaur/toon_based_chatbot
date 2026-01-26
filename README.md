# TOON Chat Application

Full-stack chat application using **TOON (Token-Oriented Object Notation)** format for 30-60% token reduction in AI interactions.

## 🎯 What is TOON?

TOON is a compact data serialization format optimized for LLM token efficiency:

**JSON (verbose):**

```json
{
  "id": 1,
  "name": "Alice",
  "profile": {
    "age": 30,
    "city": "Bengaluru"
  }
}
```

**TOON (compact):**

```
id: 1
name: Alice
profile{age,city}:
  30,Bengaluru
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Gemini API key ([Get one here](https://ai.google.dev/))

### Option 1: Automated Setup (Recommended)

```bash
# 1. Backend Setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 2. Frontend Setup
cd ../frontend
npm install
cp .env.example .env.local

# 3. Start Application (from root directory)
cd ..
./start.sh
```

The `start.sh` script will:

- ✅ Verify all dependencies
- ✅ Check configuration
- ✅ Start backend on http://localhost:8000
- ✅ Start frontend on http://localhost:3000
- ✅ Show real-time logs

### Option 2: Manual Setup

**Terminal 1 - Backend:**

```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run dev
```

**Access:**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📦 Project Structure

```
TOON/
├── backend/          # FastAPI + LangChain + Gemini
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/         # Next.js + TypeScript
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── types/
│   ├── package.json
│   └── README.md
│
├── start.sh          # Automated startup script
└── README.md         # This file
```

## ✨ Features

- **TOON Format**: 30-60% token reduction for efficient AI communication
- **Conversation History**: Persistent chat history stored in TOON format (47% space savings)
- **Message Windowing**: Only send recent N messages to LLM for token optimization
- **Multi-Session Support**: Multiple conversation sessions
- **Real-time Metrics**: Track actual token savings
- **LangChain Integration**: Powerful LLM orchestration
- **Google Gemini**: Fast, capable AI model
- **Comprehensive Logging**: Emoji-based logging system for easy monitoring
- **Error Handling**: Robust error handling on both frontend and backend
- **Type Safety**: Full TypeScript coverage

## 📊 Token Efficiency

Example savings from production use:

```
JSON:  1,234 bytes
TOON:    654 bytes
Savings: 47.0%
```

## 🛠️ Tech Stack

### Backend

- FastAPI - Modern Python web framework
- LangChain - LLM orchestration
- Google Gemini - AI model
- python-toon - Official TOON encoding/decoding for Python
- Pydantic - Data validation

### Frontend

- Next.js - React framework
- TypeScript - Type safety
- Tailwind CSS - Styling
- @toon-format/toon - Official TOON encoding/decoding for JavaScript

## 🔐 Environment Variables

### Backend (.env)

```env
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000
HISTORY_WINDOW_SIZE=10
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📚 API Endpoints

All endpoints are documented at: http://localhost:8000/docs

- `POST /api/chat` - Send chat message
- `GET /api/health` - Health check
- `GET /api/history/{session_id}` - Get conversation history
- `DELETE /api/history/{session_id}` - Clear conversation history
- `GET /` - API information

## 📈 Performance Benefits

1. **Token Reduction**: 30-60% fewer tokens per API call
2. **Storage Efficiency**: 47% less disk space for chat history
3. **Message Windowing**: Only send recent context to LLM
4. **Cost Savings**: Proportional to token reduction

## 🔧 Backend Logging

The backend includes comprehensive emoji-based logging:

```log
🚀 TOON Chat Backend Starting
📦 Model: gemini-1.5-flash
💬 Chat request received for session 'default'
👤 User message: 'Hello, how are you?'
🤖 Invoking LLM...
✅ LLM response: 'I'm doing great!'
📊 Transmission efficiency: JSON=245B, TOON=134B, Savings=45.3%
⏱️  Request completed in 1.12s
```

## 🧪 Testing

### Test Backend

```bash
curl http://localhost:8000/api/health
```

### Test Frontend

Open http://localhost:3000 and send a message

### View Logs

```bash
# Backend logs (if using start.sh)
tail -f backend.log

# Frontend logs (if using start.sh)
tail -f frontend.log
```

## 🚀 Production Deployment

### Backend (Docker)

```bash
cd backend
docker build -t toon-backend .
docker run -p 8000:8000 --env-file .env toon-backend
```

### Frontend (Vercel)

```bash
cd frontend
npm run build
vercel deploy
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Add streaming support
- [ ] Implement tool/function calling
- [ ] Add authentication
- [ ] Create more TOON components
- [ ] Performance optimizations

## 🐛 Troubleshooting

### Backend won't start

- Check that GOOGLE_API_KEY is set in `backend/.env`
- Verify virtual environment is activated
- Check `backend.log` for error details

### Frontend won't start

- Run `npm install` in frontend directory
- Check that backend is running on port 8000
- Verify `.env.local` has correct API_URL

### Connection errors

- Ensure backend is running before starting frontend
- Check CORS settings in backend `.env`
- Verify firewall allows connections on ports 3000 and 8000

## 📝 License

MIT License - feel free to use in your projects!

## 🙏 Acknowledgments

- [TOON Format](https://www.freecodecamp.org/news/what-is-toon-how-token-oriented-object-notation-could-change-how-ai-sees-data/) by the TOON community
- [LangChain](https://python.langchain.com/) for LLM orchestration
- [Google Gemini](https://ai.google.dev/) for powerful AI capabilities

---

**Built with ❤️ using TOON format for maximum efficiency**
