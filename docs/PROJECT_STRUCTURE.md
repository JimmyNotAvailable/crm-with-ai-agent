# 📂 GIẢI THÍCH CẤU TRÚC DỰ ÁN CHI TIẾT

## 🌳 Cây Thư Mục Tổng Quan

```
CRM-AI-Agent/                      # Root directory
│
├── 📁 backend/                     # Python FastAPI Backend
├── 📁 frontend/                    # React/Vue Frontend  
├── 📁 ai_modules/                  # AI Core Logic (RAG, Agent, NLQ)
├── 📁 database/                    # Database Scripts & Migrations
├── 📁 tests/                       # Testing
├── 📁 docs/                        # Documentation
├── 📁 uploads/                     # User uploaded files
├── 📁 logs/                        # Application logs
│
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment variables template
├── 📄 .gitignore                   # Git ignore rules
├── 📄 docker-compose.yml           # Docker orchestration
└── 📄 README.md                    # Project overview
```

---

## 🐍 Backend Structure (FastAPI)

### Kiến Trúc: Clean Architecture + Layered Pattern

```
backend/
├── main.py                         # 🚪 Entry point - FastAPI app
│
├── api/                            # 🌐 API Layer (HTTP Handlers)
│   └── v1/
│       ├── __init__.py
│       └── endpoints/              # API Endpoints
│           ├── auth.py             # Authentication (Login/Register)
│           ├── products.py         # Product CRUD
│           ├── orders.py           # Order management
│           ├── tickets.py          # Ticket system
│           ├── chat.py             # Chat with AI Agent
│           ├── kb.py               # Knowledge Base upload
│           └── analytics.py        # NLQ Analytics
│
├── core/                           # ⚙️ Core Configuration
│   ├── config.py                   # Settings (from .env)
│   ├── security.py                 # JWT, Password hashing
│   └── dependencies.py             # Dependency injection
│
├── models/                         # 🗄️ Database Models (SQLAlchemy ORM)
│   ├── user.py                     # User(id, email, password, role)
│   ├── product.py                  # Product(id, name, price, stock)
│   ├── order.py                    # Order(id, user_id, status, total)
│   ├── order_item.py               # OrderItem(order_id, product_id, qty)
│   ├── ticket.py                   # Ticket(id, user_id, status, priority)
│   ├── message.py                  # Message(id, ticket_id, content)
│   ├── sentiment.py                # Sentiment(id, message_id, score)
│   └── kb_article.py               # KBArticle(id, title, file_path)
│
├── schemas/                        # 📋 Pydantic Schemas (Validation)
│   ├── user.py                     # UserCreate, UserResponse, UserLogin
│   ├── product.py                  # ProductCreate, ProductUpdate, ProductResponse
│   ├── order.py                    # OrderCreate, OrderResponse
│   ├── ticket.py                   # TicketCreate, TicketResponse
│   └── chat.py                     # ChatRequest, ChatResponse
│
├── services/                       # 💼 Business Logic Layer
│   ├── auth_service.py             # Authentication logic
│   ├── product_service.py          # Product business logic
│   ├── order_service.py            # Order processing
│   ├── ticket_service.py           # Ticket routing, assignment
│   └── chat_service.py             # Chat orchestration
│
├── database/                       # 🔌 Database Connection
│   └── session.py                  # SQLAlchemy session, engine
│
└── utils/                          # 🛠️ Helper Functions
    ├── logger.py                   # Logging setup
    └── exceptions.py               # Custom exceptions
```

### Luồng Xử Lý Request (Example: Create Order)

```
1. User Request
   ↓
2. API Endpoint (api/v1/endpoints/orders.py)
   @router.post("/")
   async def create_order(order: OrderCreate, db: Session)
   ↓
3. Schema Validation (schemas/order.py)
   OrderCreate validates input
   ↓
4. Service Layer (services/order_service.py)
   def create_order_logic(order_data, db)
   - Check product availability
   - Calculate total
   - Update inventory
   ↓
5. Model/Database (models/order.py)
   new_order = Order(...)
   db.add(new_order)
   db.commit()
   ↓
6. Return Response (schemas/order.py)
   OrderResponse(id, status, total, ...)
```

---

## 🤖 AI Modules Structure

### Kiến Trúc: Modular AI Pipeline

```
ai_modules/
│
├── rag_pipeline/                   # 📚 RAG (Retrieval-Augmented Generation)
│   ├── loaders/                    # Document Loaders
│   │   ├── pdf_loader.py           # Load PDF files
│   │   ├── docx_loader.py          # Load Word documents
│   │   └── text_loader.py          # Load TXT/MD files
│   │
│   ├── chunking/                   # Text Splitting
│   │   └── text_splitter.py        # RecursiveCharacterTextSplitter
│   │
│   ├── embeddings/                 # Vector Embeddings
│   │   └── embedding_service.py    # OpenAI Embeddings / HuggingFace
│   │
│   └── retrieval/                  # Retrieval Logic
│       └── retriever.py            # Similarity search, re-ranking
│
├── agents/                         # 🦾 AI Agent System
│   ├── tools/                      # Function Calling Tools
│   │   ├── order_tools.py          # lookup_order(), cancel_order()
│   │   ├── product_tools.py        # search_products()
│   │   └── ticket_tools.py         # create_ticket()
│   │
│   ├── workflows/                  # Agent Logic (LangGraph)
│   │   └── agent_graph.py          # State graph, routing
│   │
│   └── agent.py                    # Main agent orchestrator
│
├── nlq/                            # 🔍 Natural Language Query
│   └── text_to_sql.py              # Convert text -> MySQL query
│
├── sentiment/                      # 😊😢 Sentiment Analysis
│   └── analyzer.py                 # Analyze message sentiment
│
└── vector_store/                   # 🗂️ Vector Database
    └── chroma_store.py             # ChromaDB integration
```

### RAG Pipeline Flow

```
1. Document Upload
   (PDF/DOCX file)
   ↓
2. Load Document
   loaders/pdf_loader.py → Extract text
   ↓
3. Chunk Text
   chunking/text_splitter.py → Split into chunks (1000 chars)
   ↓
4. Generate Embeddings
   embeddings/embedding_service.py → Convert to vectors
   ↓
5. Store in Vector DB
   vector_store/chroma_store.py → Save to ChromaDB
   ↓
6. User Query
   "What is the return policy?"
   ↓
7. Retrieve Context
   retrieval/retriever.py → Search similar chunks
   ↓
8. Generate Answer
   LLM (GPT-4) → Answer based on context
   ↓
9. Return with Citations
   "You can return within 30 days [Source: policy.pdf, page 3]"
```

### Agent Workflow (LangGraph)

```
┌─────────────┐
│ User Input  │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Classify Intent  │ (LLM)
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌──────────┐
│  RAG   │  │  Tools   │
│  Node  │  │  Node    │
└────┬───┘  └────┬─────┘
     │           │
     │      ┌────┴─────┐
     │      │          │
     │      ▼          ▼
     │  ┌────────┐  ┌──────────┐
     │  │ Order  │  │ Product  │
     │  │ Tools  │  │ Search   │
     │  └────┬───┘  └────┬─────┘
     │       │           │
     └───────┴───────────┘
              │
              ▼
      ┌──────────────┐
      │   Response   │
      └──────────────┘
```

---

## 💻 Frontend Structure (React)

```
frontend/
├── public/                         # Static files
│   ├── index.html
│   └── favicon.ico
│
└── src/
    ├── App.jsx                     # Main app component
    ├── main.jsx                    # Entry point
    │
    ├── components/                 # UI Components
    │   ├── chat/                   # Chat Components
    │   │   ├── ChatWidget.jsx      # Floating chat button
    │   │   ├── ChatWindow.jsx      # Chat interface
    │   │   ├── MessageList.jsx     # Message display
    │   │   └── MessageInput.jsx    # Input box
    │   │
    │   ├── dashboard/              # Dashboard Components
    │   │   ├── Sidebar.jsx         # Navigation sidebar
    │   │   ├── Header.jsx          # Top header
    │   │   ├── StatCard.jsx        # Stats display
    │   │   └── Chart.jsx           # Chart component
    │   │
    │   └── common/                 # Shared Components
    │       ├── Button.jsx
    │       ├── Input.jsx
    │       ├── Modal.jsx
    │       └── Table.jsx
    │
    ├── pages/                      # Page Views
    │   ├── Login.jsx               # Login page
    │   ├── Dashboard.jsx           # Main dashboard
    │   ├── Products.jsx            # Product listing
    │   ├── ProductDetail.jsx       # Product details
    │   ├── Orders.jsx              # Order list
    │   ├── OrderDetail.jsx         # Order details
    │   ├── Tickets.jsx             # Ticket list
    │   └── Analytics.jsx           # Analytics dashboard
    │
    ├── services/                   # API Services
    │   ├── api.js                  # Axios instance
    │   ├── authService.js          # Auth API calls
    │   ├── productService.js       # Product API calls
    │   ├── orderService.js         # Order API calls
    │   └── chatService.js          # Chat API calls
    │
    ├── store/                      # State Management (Zustand)
    │   ├── authStore.js            # Auth state
    │   ├── chatStore.js            # Chat state
    │   └── cartStore.js            # Shopping cart state
    │
    ├── utils/                      # Utilities
    │   ├── formatters.js           # Date, currency formatters
    │   └── validators.js           # Form validation
    │
    └── assets/                     # Static assets
        ├── styles/                 # CSS/SCSS files
        └── images/                 # Images
```

### Component Communication Flow

```
Page (e.g., Dashboard.jsx)
  ↓ uses
Store (authStore.js) ← API calls → Backend
  ↓ provides data
Components (StatCard, Chart)
  ↓ user action
Service (orderService.js) → API call → Backend
```

---

## 🗄️ Database Structure

```
database/
├── migrations/                     # Alembic migrations
│   ├── versions/                   # Migration files
│   │   └── 001_initial.py          # Initial schema
│   └── env.py                      # Alembic config
│
├── seeds/                          # Seed data
│   ├── fake_data.py                # Generate fake data (Faker)
│   └── init_data.py                # Initial data (categories, etc.)
│
├── schemas/                        # SQL schema files
│   └── init.sql                    # MySQL schema
│
└── scripts/                        # Utility scripts
    ├── backup.sh                   # Database backup
    └── restore.sh                  # Database restore
```

### Database Schema (MySQL)

**Core Tables:**

```sql
-- Users
users (id, email, password_hash, role, created_at)

-- Products
products (id, name, description, price, stock, created_at)

-- Orders
orders (id, user_id, status, total, created_at)
order_items (id, order_id, product_id, quantity, price)

-- Tickets (Customer Support)
tickets (id, user_id, subject, status, priority, created_at)
messages (id, ticket_id, sender_id, content, created_at)
sentiments (id, message_id, score, label)

-- Knowledge Base (RAG)
kb_articles (id, title, file_path, created_at)
```

---

## 🧪 Testing Structure

```
tests/
├── unit/                           # Unit tests
│   ├── test_auth.py                # Auth service tests
│   ├── test_products.py            # Product service tests
│   └── test_rag_pipeline.py        # RAG pipeline tests
│
└── integration/                    # Integration tests
    ├── test_api_auth.py            # Auth API tests
    ├── test_api_orders.py          # Order API tests
    └── test_agent_workflow.py      # Agent end-to-end tests
```

---

## 📚 Documentation Structure

```
docs/
├── QUICKSTART.md                   # Quick start guide
├── GETTING_STARTED.md              # Detailed setup guide
├── ROADMAP.md                      # 8-week roadmap
├── PROJECT_STRUCTURE.md            # This file
├── API.md                          # API documentation (TODO)
└── DEPLOYMENT.md                   # Deployment guide (TODO)
```

---

## 🎯 Mối Quan Hệ Giữa Các Module

```
┌─────────────────────────────────────────────┐
│             Frontend (React)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Dashboard │  │ Products │  │   Chat   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼────────────┼─────────────┼──────────┘
        │            │              │
        │ HTTP/REST  │              │ WebSocket (optional)
        ▼            ▼              ▼
┌────────────────────────────────────────────┐
│         Backend (FastAPI)                   │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐   │
│  │   API   │  │Services │  │  Models  │   │
│  └────┬────┘  └────┬────┘  └────┬─────┘   │
└───────┼────────────┼────────────┼──────────┘
        │            │             │
        │            └─────┬───────┘
        │                  │
        ▼                  ▼
   ┌─────────┐      ┌──────────┐
   │AI Modules│      │  MySQL  │
   │  (RAG,   │      │ Database │
   │  Agent)  │      └──────────┘
   └────┬────┘
        │
        ▼
   ┌─────────┐
   │ChromaDB │
   │ (Vector)│
   └─────────┘
```

---

## 💡 Best Practices Áp Dụng

### 1. Clean Architecture
- **Separation of Concerns**: API → Service → Model
- **Dependency Inversion**: High-level không phụ thuộc low-level

### 2. Modular Design
- Mỗi module có trách nhiệm riêng
- Dễ dàng test, maintain, extend

### 3. Configuration Management
- Tất cả config trong `.env`
- Không hardcode credentials

### 4. Error Handling
- Custom exceptions
- Proper HTTP status codes
- User-friendly error messages

### 5. Security
- JWT for authentication
- Password hashing (bcrypt)
- SQL injection prevention (ORM)
- CORS configuration

---

**Hy vọng tài liệu này giúp bạn hiểu rõ cấu trúc dự án! 🚀**
