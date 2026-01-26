# TOON Chat Backend

FastAPI backend with LangChain integration and Google Gemini LLM using standard TOON format for efficient token usage.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your Google Gemini API key:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash  # or gemini-1.5-pro
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
ALLOWED_ORIGINS=http://localhost:3000  # Frontend URL(s), comma-separated
```

### 3. Run the Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at `http://localhost:8000`

## 📡 API Endpoints

### POST `/api/chat`

Main chat endpoint with TOON encoding/decoding.

**Request Body:**
```json
{
  "messages_toon": "messages[2]{role,content}:\n  user,Hello\n  assistant,Hi there!",
  "use_tools": false
}
```

**Response:**
```json
{
  "response_toon": "role: assistant\ncontent: I'm doing great, how can I help you?"
}
```

### GET `/api/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model": "gemini-1.5-flash",
  "toon_version": "standard",
  "api_key_configured": true
}
```

### GET `/`

Root endpoint with API information.

## 🧩 Project Structure

```
backend/
├── main.py              # FastAPI application with TOON integration
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── README.md
```

## 📝 TOON Format

This backend uses **standard TOON (Token-Oriented Object Notation)** format via the `python-toon` library.

### What is TOON?

TOON is a compact data serialization format designed for AI interactions, reducing token usage by 30-50% compared to JSON.

**Example:**

**JSON:**
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

**TOON:**
```
id: 1
name: Alice
profile{age,city}:
  30,Bengaluru
```

### Usage in Backend

```python
from toon import encode, decode

# Decode incoming TOON request
messages = decode(request.messages_toon)

# Encode response to TOON
response_toon = encode({
    "role": "assistant",
    "content": "Hello!"
})
```

## 🔧 LangChain Integration

The backend uses LangChain for LLM orchestration:

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7
)

# Generate response
response = await llm.ainvoke(messages)
```

## 📊 Logging

Comprehensive logging is built into the backend for observability.

### Configuration

Set log level in `.env`:
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### What Gets Logged

- **Application startup**: Model, API key status, log level
- **Request handling**: TOON decoding/encoding process
- **LLM responses**: Response previews
- **Errors**: Full stack traces with context

### Example Logs

```
2024-01-25 16:38:00 - __main__ - INFO - ============================================================
2024-01-25 16:38:00 - __main__ - INFO - TOON Chat Backend Starting
2024-01-25 16:38:00 - __main__ - INFO - Model: gemini-1.5-flash
2024-01-25 16:38:01 - __main__ - INFO - Chat request received
2024-01-25 16:38:01 - __main__ - INFO - Decoding TOON input: messages[2]{role,content}:...
2024-01-25 16:38:01 - __main__ - INFO - Decoded 2 messages
2024-01-25 16:38:02 - __main__ - INFO - LLM response received: I'd be happy to help you...
2024-01-25 16:38:02 - __main__ - INFO - Encoded response to TOON: role: assistant...
```

## 🔐 Security Considerations

1. **API Key Protection**: Never commit `.env` file
2. **CORS**: Configure allowed origins in `.env`
3. **Input Validation**: Pydantic models validate requests
4. **Error Handling**: Errors returned in TOON format

## 📚 Dependencies

- **fastapi>=0.109.0**: Modern web framework
- **uvicorn>=0.27.0**: ASGI server
- **langchain>=0.3.0**: LLM orchestration
- **langchain-google-genai>=2.0.0**: Gemini integration
- **python-dotenv>=1.0.0**: Environment variable management
- **pydantic>=2.5.0**: Data validation
- **python-toon>=0.1.0**: TOON encode/decode library

## 🚀 Production Deployment

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t toon-backend .
docker run -p 8000:8000 --env-file .env toon-backend
```

### Environment Variables for Production

```env
GOOGLE_API_KEY=xxx
GEMINI_MODEL=gemini-1.5-flash
ALLOWED_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO
```

## 🧪 Testing

Create `test_main.py`:
```python
from fastapi.testclient import TestClient
from main import app
from toon import encode

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat():
    messages = [{"role": "user", "content": "Hello"}]
    messages_toon = encode(messages)

    response = client.post(
        "/api/chat",
        json={"messages_toon": messages_toon, "use_tools": False}
    )
    assert response.status_code == 200
    assert "response_toon" in response.json()
```

Run tests:
```bash
pip install pytest
pytest test_main.py
```

## 📖 Further Reading

- [TOON Format Article](https://www.freecodecamp.org/news/what-is-toon-how-token-oriented-object-notation-could-change-how-ai-sees-data/)
- [Python TOON Library](https://pypi.org/project/python-toon/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Google Gemini API](https://ai.google.dev/docs)

---

Happy coding! 🚀
