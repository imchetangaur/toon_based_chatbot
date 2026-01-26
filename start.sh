#!/bin/bash

echo "========================================="
echo "🚀 TOON Chat - Starting Application"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if backend dependencies are installed
if [ ! -d "backend/venv" ]; then
    echo -e "${RED}❌ Backend virtual environment not found${NC}"
    echo "Please run: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${RED}❌ Frontend node_modules not found${NC}"
    echo "Please run: cd frontend && npm install"
    exit 1
fi

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  Backend .env not found${NC}"
    echo "Creating from template..."
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}⚠️  Please edit backend/.env and add your GOOGLE_API_KEY${NC}"
    echo "Then run this script again."
    exit 1
fi

# Check if API key is set
if ! grep -q "GOOGLE_API_KEY=AIza" backend/.env && ! grep -q "GOOGLE_API_KEY=your_gemini" backend/.env; then
    API_KEY_SET=true
else
    echo -e "${YELLOW}⚠️  GOOGLE_API_KEY not configured in backend/.env${NC}"
    echo "Please add your API key and run this script again."
    exit 1
fi

# Create frontend .env.local if it doesn't exist
if [ ! -f "frontend/.env.local" ]; then
    echo -e "${BLUE}📝 Creating frontend/.env.local${NC}"
    cp frontend/.env.example frontend/.env.local
fi

echo -e "${GREEN}✅ All dependencies and configurations found${NC}"
echo ""
echo "========================================="
echo "Starting servers..."
echo "========================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "========================================="
    echo "🛑 Stopping servers..."
    echo "========================================="
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend in background
echo -e "${BLUE}🐍 Starting Backend (http://localhost:8000)${NC}"
cd backend
source venv/bin/activate
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend failed to start. Check backend.log for errors${NC}"
    kill $BACKEND_PID 2>/dev/null
    tail -20 backend.log
    exit 1
fi

echo -e "${GREEN}✅ Backend started successfully${NC}"
echo ""

# Start frontend in background
echo -e "${BLUE}⚛️  Starting Frontend (http://localhost:3000)${NC}"
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================="
echo -e "${GREEN}✅ Application Started Successfully!${NC}"
echo "========================================="
echo ""
echo -e "${BLUE}🌐 Frontend:${NC} http://localhost:3000"
echo -e "${BLUE}🔧 Backend:${NC}  http://localhost:8000"
echo -e "${BLUE}📚 API Docs:${NC} http://localhost:8000/docs"
echo ""
echo "📋 Logs:"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Wait for user interrupt
wait
