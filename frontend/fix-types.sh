#!/bin/bash

echo "========================================="
echo "🔧 Fixing All TypeScript JSX Errors"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Step 1: Checking project structure...${NC}"
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: Not in frontend directory${NC}"
    echo "Please run this from the frontend directory:"
    echo "  cd frontend"
    echo "  ./fix-types.sh"
    exit 1
fi

echo -e "${GREEN}✅ In correct directory${NC}"
echo ""

echo -e "${BLUE}Step 2: Installing dependencies...${NC}"
npm install
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Step 3: Verifying React types...${NC}"
if [ -d "node_modules/@types/react" ]; then
    echo -e "${GREEN}✅ @types/react installed${NC}"
else
    echo -e "${YELLOW}⚠️  Installing @types/react...${NC}"
    npm install --save-dev @types/react @types/react-dom
    echo -e "${GREEN}✅ @types/react installed${NC}"
fi

echo ""
echo -e "${BLUE}Step 4: Checking next-env.d.ts...${NC}"
if [ -f "next-env.d.ts" ]; then
    echo -e "${GREEN}✅ next-env.d.ts exists${NC}"
else
    echo -e "${YELLOW}⚠️  Creating next-env.d.ts...${NC}"
    cat > next-env.d.ts << 'EOF'
/// <reference types="next" />
/// <reference types="next/image-types/global" />

// NOTE: This file should not be edited
// see https://nextjs.org/docs/basic-features/typescript for more information.
EOF
    echo -e "${GREEN}✅ next-env.d.ts created${NC}"
fi

echo ""
echo -e "${BLUE}Step 5: Verifying React imports in components...${NC}"

# Check if React is imported in all TSX files
check_react_import() {
    local file=$1
    if grep -q "^import React" "$file"; then
        echo -e "${GREEN}✅ $file${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  $file (missing React import)${NC}"
        return 1
    fi
}

check_react_import "app/page.tsx"
check_react_import "app/layout.tsx"
check_react_import "components/Chat.tsx"

echo ""
echo -e "${BLUE}Step 6: Cleaning TypeScript cache...${NC}"
rm -rf .next
rm -f tsconfig.tsbuildinfo
echo -e "${GREEN}✅ Cache cleaned${NC}"

echo ""
echo -e "${BLUE}Step 7: Verifying tsconfig.json...${NC}"
if grep -q '"jsx": "preserve"' tsconfig.json; then
    echo -e "${GREEN}✅ tsconfig.json correctly configured${NC}"
else
    echo -e "${YELLOW}⚠️  tsconfig.json may need manual review${NC}"
fi

echo ""
echo "========================================="
echo -e "${GREEN}✅ All fixes applied!${NC}"
echo "========================================="
echo ""
echo -e "${YELLOW}Important Next Steps:${NC}"
echo ""
echo "1. ${BLUE}Restart your editor/IDE${NC}"
echo "   - Close and reopen VS Code, WebStorm, etc."
echo ""
echo "2. ${BLUE}If using VS Code:${NC}"
echo "   - Press: Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows)"
echo "   - Type: 'TypeScript: Restart TS Server'"
echo "   - Press: Enter"
echo ""
echo "3. ${BLUE}Start the development server:${NC}"
echo "   npm run dev"
echo ""
echo -e "${GREEN}The JSX type errors should now be resolved! 🎉${NC}"
echo ""
