# TOON Chat Frontend

Next.js + TypeScript frontend with dynamic component rendering based on TOON tokens.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Open `http://localhost:3000` in your browser.

## 📁 Project Structure

```
frontend/
├── app/
│   ├── page.tsx           # Home page (Chat component)
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
│
├── components/
│   ├── Chat.tsx           # Main chat interface
│   └── ToonRenderer.tsx   # Token → Component mapper
│
├── lib/
│   └── toonParser.ts      # TOON parsing logic
│
├── types/
│   └── toon.ts            # TypeScript type definitions
│
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## 🧩 Core Components

### 1. Chat Component (`components/Chat.tsx`)

Main chat interface that handles:

- Message state management
- Streaming from backend
- User input
- Auto-scrolling

**Key Features:**

```typescript
const [messages, setMessages] = useState<ToonMessage[]>([]);
const [isStreaming, setIsStreaming] = useState(false);
const streamParserRef = useRef<ToonStreamParser>(new ToonStreamParser());

// Send message and handle streaming
const sendMessage = async () => {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    body: JSON.stringify({ messages, stream: true }),
  });

  const reader = response.body!.getReader();
  // Parse SSE stream incrementally...
};
```

### 2. ToonRenderer Component (`components/ToonRenderer.tsx`)

Renders TOON tokens as React components.

**Component Mapping:**

```typescript
function TokenComponent({ token }: { token: ToonToken }) {
  switch (token.type) {
    case "text": return <TextToken />;
    case "code": return <CodeToken />;
    case "list": return <ListToken />;
    case "alert": return <AlertToken />;
    case "card": return <CardToken />;
    case "chart": return <ChartToken />;
    case "thinking": return <ThinkingToken />;
    case "tool_call": return <ToolCallToken />;
    case "tool_result": return <ToolResultToken />;
  }
}
```

### 3. TOON Parser (`lib/toonParser.ts`)

Uses official `@toon-format/toon` library for encoding/decoding.

**Encoding:**

```typescript
import { encode, decode } from "@toon-format/toon";

export function encodeToon(messages: ChatMessage[]): string {
  return encode(messages);
}
```

**Decoding:**

```typescript
export function decodeToon(toonString: string): ChatMessage[] {
  const decoded = decode(toonString);
  return Array.isArray(decoded) ? decoded : [decoded];
}
```

## 🎨 Component Reference

### Text Component

Renders plain text paragraphs.

**TOON Input:**

```
@text
"Hello world"
```

**Rendered Output:**

```tsx
<p className="text-gray-800 dark:text-gray-200">Hello world</p>
```

### Code Component

Syntax-highlighted code blocks.

**TOON Input:**

```
@code(lang=python)
"def hello(): print('hi')"
```

**Rendered Output:**

- Language badge (e.g., "python")
- Syntax-highlighted code
- Dark theme by default

**Dependencies:**

- `react-syntax-highlighter`
- `vscDarkPlus` theme

### List Component

Bullet point lists.

**TOON Input:**

```
@list
- "Item 1"
- "Item 2"
```

**Rendered Output:**

```tsx
<ul className="list-disc list-inside space-y-1">
  <li>Item 1</li>
  <li>Item 2</li>
</ul>
```

### Alert Component

Colored alert boxes with icons.

**TOON Input:**

```
@alert(type=warning)
"Be careful!"
```

**Types:** `info`, `warning`, `error`, `success`

**Rendered Output:**

- Colored border (left side)
- Icon emoji
- Styled text

### Card Component

Highlighted content cards.

**TOON Input:**

```
@card(title="Pro Tip", subtitle="Best practices")
"Always validate user input"
```

**Rendered Output:**

- Title and optional subtitle
- Content body
- Hover effect
- Shadow styling

### Chart Component

Data visualizations using Recharts.

**TOON Input:**

```
@chart(type=bar)
"{
  \"labels\": [\"Jan\", \"Feb\", \"Mar\"],
  \"values\": [10, 20, 15],
  \"title\": \"Sales\"
}"
```

**Supported Types:**

- `bar`: Bar chart
- `line`: Line chart
- `pie`: Pie chart

**Dependencies:** `recharts`

### Thinking Component

Collapsible reasoning display.

**TOON Input:**

```
@thinking
"Let me break this down step by step..."
```

**Rendered Output:**

- Collapsible `<details>` element
- Brain emoji icon
- Styled in purple theme
- Italic text

### Tool Components

Tool execution visualization.

**Tool Call:**

```
@tool(name=search)
"{\"query\": \"LangChain\"}"
```

**Tool Result:**

```
@tool_result(name=search)
"Found 3 results..."
```

**Rendered Output:**

- Tool call: Blue box with wrench icon
- Tool result: Green box with sparkles icon
- JSON pretty-printing

## 🎨 Styling

### Tailwind CSS

The project uses Tailwind CSS for styling.

**Color Scheme:**

- Primary: Blue (`bg-blue-600`)
- Success: Green
- Warning: Yellow
- Error: Red
- Info: Blue

**Dark Mode:**
All components support dark mode using Tailwind's `dark:` prefix.

### Custom Styles

Global styles in `app/globals.css`:

- Custom scrollbar
- Animation delays for loading dots
- CSS variables for theme colors

## 📱 Responsive Design

The UI is fully responsive:

- Mobile: Single column, full-width messages
- Tablet: Constrained width (max-w-4xl)
- Desktop: Centered layout with margins

## 🔄 Streaming Implementation

### SSE Parsing

```typescript
const reader = response.body!.getReader();
const decoder = new TextDecoder();

while (true) {
  const { value, done } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split("\n");

  for (const line of lines) {
    const data = parseSSEData(line); // Extract "data: ..." content
    if (data) {
      const tokens = streamParserRef.current.addChunk(data);
      setMessages(/* update with new tokens */);
    }
  }
}
```

### Incremental Rendering

Tokens are parsed and rendered incrementally as they arrive:

1. Chunk arrives from backend
2. Added to buffer in `ToonStreamParser`
3. Buffer parsed into tokens
4. React state updated
5. UI re-renders with new content

## 🔧 Configuration

### Environment Variables

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Future: Add authentication, analytics, etc.
```

### TypeScript Configuration

Strict mode enabled in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "skipLibCheck": true,
    "esModuleInterop": true
  }
}
```

## 🚀 Build for Production

```bash
# Build optimized production bundle
npm run build

# Run production server
npm start
```

**Output:**

- Static assets in `.next/static/`
- Optimized JavaScript bundles
- Image optimization
- Font optimization

## 🧪 Testing (Future Enhancement)

### Unit Tests with Jest

```bash
npm install --save-dev jest @testing-library/react
```

Test example:

```typescript
import { parseToon } from "@/lib/toonParser";

describe("TOON Parser", () => {
  it("should parse text token", () => {
    const input = '@text\n"Hello"';
    const tokens = parseToon(input);
    expect(tokens[0]).toEqual({
      type: "text",
      content: "Hello",
    });
  });
});
```

### E2E Tests with Playwright

```bash
npm install --save-dev @playwright/test
```

## 📊 Performance Optimizations

### Current

- Server-side rendering (SSR) disabled for Chat component
- Client-side only (`"use client"`)
- Efficient re-renders with React keys
- Memoization opportunities (not yet implemented)

### Future Improvements

- [ ] React.memo for ToonRenderer components
- [ ] Virtual scrolling for long chat histories
- [ ] Lazy loading for code highlighter
- [ ] Web Workers for parsing large responses

## 🎯 Type Safety

Full TypeScript coverage:

```typescript
// types/toon.ts
export type ToonToken =
  | { type: "text"; content: string }
  | { type: "code"; lang: string; content: string }
  | { type: "list"; items: string[] };
// ... more types

export interface ToonMessage {
  role: "user" | "assistant";
  tokens: ToonToken[];
  rawContent?: string;
}
```

Benefits:

- Compile-time type checking
- IntelliSense support
- Refactoring safety
- Self-documenting code

## 🔐 Security

### XSS Prevention

- React automatically escapes content
- Code blocks use `react-syntax-highlighter` (safe)
- No `dangerouslySetInnerHTML` used

### API Security

- CORS configured on backend
- No sensitive data in client code
- Environment variables for config

## 📦 Dependencies

### Core

- `next`: React framework
- `react`: UI library
- `react-dom`: DOM rendering
- `@toon-format/toon`: Official TOON encoding/decoding library

### UI & Styling

- `tailwindcss`: Utility-first CSS

### Development

- `typescript`: Type safety
- `eslint`: Linting
- `autoprefixer`: CSS prefixing

## 🚀 Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

CMD ["npm", "start"]
```

### Environment Variables in Production

Set in your hosting platform:

```
NEXT_PUBLIC_API_URL=https://your-api.com
```

## 🎓 Learning Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Recharts Guide](https://recharts.org/en-US/)

## 🔄 Extending the Frontend

### Adding New Token Types

1. **Define Type** (`types/toon.ts`):

```typescript
export type ToonToken =
  | { type: "table"; headers: string[]; rows: string[][] }
  | // ... existing types
```

2. **Update Parser** (`lib/toonParser.ts`):

```typescript
else if (line.startsWith("@table")) {
  // Parse table token
}
```

3. **Create Component** (`components/ToonRenderer.tsx`):

```typescript
function TableToken({ headers, rows }) {
  return (
    <table className="...">
      <thead>
        {headers.map(h => <th>{h}</th>)}
      </thead>
      <tbody>
        {rows.map(row => <tr>{row.map(cell => <td>{cell}</td>)}</tr>)}
      </tbody>
    </table>
  );
}
```

4. **Add to Renderer**:

```typescript
case "table":
  return <TableToken headers={token.headers} rows={token.rows} />;
```

---

Happy building! 🚀
