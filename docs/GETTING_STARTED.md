# 🚀 HƯỚNG DẪN BẮT ĐÀU DỰ ÁN CRM-AI-AGENT

## 📋 Mục Lục
1. [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
2. [Thiết lập môi trường](#thiết-lập-môi-trường)
3. [Cấu trúc dự án](#cấu-trúc-dự-án)
4. [Lộ trình thực hiện](#lộ-trình-thực-hiện)
5. [Hướng dẫn phát triển](#hướng-dẫn-phát-triển)

---

## 🖥️ Yêu Cầu Hệ Thống

### Bắt buộc
- **Python**: 3.10 hoặc cao hơn
- **Node.js**: 18.x hoặc cao hơn (cho Frontend)
- **MySQL**: 8.0 hoặc cao hơn
- **Git**: Để quản lý version control

### Khuyến nghị
- **Docker & Docker Compose**: Để chạy toàn bộ hệ thống dễ dàng
- **VS Code**: Editor được khuyến nghị với các extensions:
  - Python
  - Pylance
  - Docker
  - ESLint (cho Frontend)

### API Keys cần thiết
- **OpenAI API Key**: Đăng ký tại https://platform.openai.com/
  - Hoặc có thể dùng **Google Gemini API** (miễn phí hơn)
  - Hoặc **Claude API** từ Anthropic

---

## ⚙️ Thiết Lập Môi Trường

### Bước 1: Clone và Chuẩn Bị

```bash
# Đã có thư mục CRM-AI-Agent
cd "d:\Bai Luan\Nam 2025 - 2026\Hoc Ky I\CS434\CS434\CRM-AI-Agent"

# Tạo file .env từ template
cp .env.example .env
```

### Bước 2: Cấu Hình File .env

Mở file `.env` và điền các thông tin quan trọng:

```env
# Quan trọng nhất - API Key cho LLM
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx

# Mật khẩu MySQL
MYSQL_PASSWORD=your_secure_password_here

# Secret key cho JWT (tạo random string)
SECRET_KEY=your-very-secret-key-min-32-characters
```

**Lưu ý**: 
- Không commit file `.env` lên Git
- `SECRET_KEY` nên dùng tool tạo random: `openssl rand -hex 32`

### Bước 3: Cài Đặt Dependencies

#### Option 1: Dùng Docker (Dễ nhất - Khuyến nghị)

```bash
# Đảm bảo Docker Desktop đang chạy
docker --version
docker-compose --version

# Khởi động tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f backend
```

#### Option 2: Cài Đặt Manual (Cho Development)

**Backend:**

```bash
cd backend

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat

# Cài đặt packages
pip install -r ../requirements.txt
```

**Frontend:**

```bash
cd frontend

# Cài đặt dependencies
npm install
# Hoặc dùng yarn
yarn install
```

**MySQL:**

```bash
# Cài MySQL 8.0 từ:
# https://dev.mysql.com/downloads/installer/

# Hoặc dùng Docker:
docker run --name crm_mysql \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=crm_ai_db \
  -e MYSQL_USER=crm_user \
  -e MYSQL_PASSWORD=your_secure_password_here \
  -p 3306:3306 \
  -d mysql:8.0
```

---

## 📁 Cấu Trúc Dự Án Chi Tiết

```
CRM-AI-Agent/
│
├── backend/                    # 🐍 Python FastAPI Backend
│   ├── api/v1/endpoints/       # API Routes (Phase 1)
│   │   ├── auth.py            # TODO: Authentication endpoints
│   │   ├── products.py        # TODO: Product CRUD
│   │   ├── orders.py          # TODO: Order management
│   │   ├── chat.py            # TODO: Chat with AI Agent
│   │   ├── kb.py              # TODO: Knowledge Base upload
│   │   └── analytics.py       # TODO: NLQ Analytics
│   │
│   ├── core/                   # Configuration & Security
│   │   ├── config.py          # ✅ Settings (đã tạo)
│   │   ├── security.py        # TODO: JWT, Password hashing
│   │   └── dependencies.py    # TODO: Dependency injection
│   │
│   ├── models/                 # SQLAlchemy ORM Models (Phase 1)
│   │   ├── user.py            # TODO: User model
│   │   ├── product.py         # TODO: Product model
│   │   ├── order.py           # TODO: Order model
│   │   ├── ticket.py          # TODO: Ticket model
│   │   └── kb_article.py      # TODO: Knowledge Base article
│   │
│   ├── schemas/                # Pydantic Schemas (Phase 1)
│   │   └── ...                # TODO: Request/Response schemas
│   │
│   ├── services/               # Business Logic (Phase 1-4)
│   │   └── ...                # TODO: Service layer
│   │
│   ├── database/               # Database Connection
│   │   └── session.py         # TODO: SQLAlchemy session
│   │
│   ├── main.py                 # ✅ FastAPI app entry point
│   └── Dockerfile              # ✅ Docker configuration
│
├── ai_modules/                 # 🤖 AI Core Logic
│   ├── rag_pipeline/           # Phase 2: RAG System
│   │   ├── loaders/
│   │   │   ├── pdf_loader.py      # TODO: Load PDF files
│   │   │   └── docx_loader.py     # TODO: Load Word files
│   │   ├── chunking/
│   │   │   └── text_splitter.py   # TODO: Chunk text
│   │   ├── embeddings/
│   │   │   └── embedding_service.py # TODO: Generate embeddings
│   │   └── retrieval/
│   │       └── retriever.py       # TODO: Similarity search
│   │
│   ├── agents/                 # Phase 3: AI Agent
│   │   ├── tools/
│   │   │   ├── order_tools.py     # TODO: Order lookup/cancel
│   │   │   └── product_tools.py   # TODO: Product recommendation
│   │   ├── workflows/
│   │   │   └── agent_graph.py     # TODO: LangGraph workflow
│   │   └── agent.py               # TODO: Main agent logic
│   │
│   ├── nlq/                    # Phase 4: Natural Language Query
│   │   └── text_to_sql.py     # TODO: Convert text to SQL
│   │
│   ├── sentiment/              # Phase 3: Sentiment Analysis
│   │   └── analyzer.py        # TODO: Analyze sentiment
│   │
│   └── vector_store/           # Phase 2: Vector Database
│       └── chroma_store.py    # TODO: ChromaDB integration
│
├── database/                   # 🗄️ Database Scripts
│   ├── migrations/             # Alembic migrations
│   ├── seeds/
│   │   └── fake_data.py       # TODO: Generate fake data
│   ├── schemas/
│   │   └── init.sql           # TODO: Initial schema
│   └── scripts/
│       └── backup.sh          # TODO: Backup script
│
├── frontend/                   # 💻 React/Vue Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/          # Phase 2: Chat UI
│   │   │   ├── dashboard/     # Phase 1: Dashboard
│   │   │   └── common/        # Phase 1: Shared components
│   │   ├── pages/             # Phase 1: Pages
│   │   ├── services/          # Phase 1: API calls
│   │   └── App.jsx            # TODO: Main app
│   └── package.json           # TODO: Dependencies
│
├── tests/                      # 🧪 Testing
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
│
├── docs/                       # 📚 Documentation
│   └── api_specs.md           # TODO: API documentation
│
├── .env.example                # ✅ Environment template
├── .gitignore                  # ✅ Git ignore rules
├── docker-compose.yml          # ✅ Docker orchestration
├── requirements.txt            # ✅ Python dependencies
└── README.md                   # ✅ Project overview
```

**Chú thích:**
- ✅ = Đã tạo sẵn
- TODO = Cần làm trong các Phase tương ứng

---

## 🗓️ Lộ Trình Thực Hiện

### 📍 PHASE 1: Core Foundation (Tuần 1-2)

**Mục tiêu**: Xây dựng khung Backend + Frontend cơ bản

#### Checklist Backend:

- [ ] **1.1 Database Setup**
  ```bash
  # Tạo file database/schemas/init.sql
  # Chạy migrations
  cd backend
  alembic init alembic
  alembic revision --autogenerate -m "Initial schema"
  alembic upgrade head
  ```

- [ ] **1.2 Models (SQLAlchemy)**
  - `backend/models/user.py`: User model với roles (Admin/Staff/Customer)
  - `backend/models/product.py`: Product model
  - `backend/models/order.py`: Order model
  - `backend/models/ticket.py`: Ticket model

- [ ] **1.3 Schemas (Pydantic)**
  - Request/Response schemas cho từng model

- [ ] **1.4 API Endpoints**
  - `POST /api/v1/auth/register`: Đăng ký
  - `POST /api/v1/auth/login`: Đăng nhập (trả về JWT)
  - `GET /api/v1/products`: List products (có pagination)
  - `POST /api/v1/orders`: Tạo đơn hàng
  - `GET /api/v1/orders/{id}`: Chi tiết đơn hàng

- [ ] **1.5 Seed Data**
  ```bash
  python database/seeds/fake_data.py
  # Tạo 100 products, 1000 orders
  ```

#### Checklist Frontend:

- [ ] **1.6 Setup Project**
  ```bash
  cd frontend
  # React:
  npx create-react-app .
  # Hoặc Vue:
  npm create vue@latest .
  ```

- [ ] **1.7 Components**
  - Layout/Header/Sidebar
  - Product List
  - Order Detail
  - Login Form

- [ ] **1.8 API Integration**
  - Axios/Fetch setup
  - Call Backend APIs

**Deliverable**: Hệ thống có thể đăng ký, đăng nhập, xem sản phẩm, tạo đơn hàng.

---

### 📍 PHASE 2: RAG System (Tuần 3-4)

**Mục tiêu**: Chatbot trả lời FAQ từ tài liệu

#### Checklist:

- [ ] **2.1 Vector Store Setup**
  ```python
  # ai_modules/vector_store/chroma_store.py
  import chromadb
  # Initialize ChromaDB
  ```

- [ ] **2.2 Document Loaders**
  ```python
  # ai_modules/rag_pipeline/loaders/pdf_loader.py
  from langchain.document_loaders import PyPDFLoader
  ```

- [ ] **2.3 Chunking**
  ```python
  # ai_modules/rag_pipeline/chunking/text_splitter.py
  from langchain.text_splitter import RecursiveCharacterTextSplitter
  ```

- [ ] **2.4 Embeddings**
  ```python
  # ai_modules/rag_pipeline/embeddings/embedding_service.py
  from langchain.embeddings import OpenAIEmbeddings
  ```

- [ ] **2.5 Upload API**
  ```python
  # backend/api/v1/endpoints/kb.py
  @router.post("/upload")
  async def upload_document(file: UploadFile):
      # Save file -> Load -> Chunk -> Embed -> Store
  ```

- [ ] **2.6 RAG Chat API**
  ```python
  # backend/api/v1/endpoints/chat.py
  @router.post("/")
  async def chat(message: str):
      # Retrieve context -> Generate answer
  ```

- [ ] **2.7 Chat Widget (Frontend)**
  - Floating chat button
  - Chat interface

**Deliverable**: Upload PDF chính sách -> Chat hỏi về chính sách -> Bot trả lời đúng.

---

### 📍 PHASE 3: AI Agent (Tuần 5-6)

**Mục tiêu**: Agent có thể thực hiện hành động

#### Checklist:

- [ ] **3.1 Define Tools**
  ```python
  # ai_modules/agents/tools/order_tools.py
  def lookup_order(order_id: str):
      # Query database
      
  def cancel_order(order_id: str):
      # Update order status
  ```

- [ ] **3.2 Agent Logic (LangGraph)**
  ```python
  # ai_modules/agents/workflows/agent_graph.py
  from langgraph.graph import StateGraph
  ```

- [ ] **3.3 Sentiment Analysis**
  ```python
  # ai_modules/sentiment/analyzer.py
  from textblob import TextBlob
  ```

- [ ] **3.4 Smart Routing**
  - Phân loại ticket tự động

**Deliverable**: 
- User: "Hủy đơn #123" -> Agent tự hủy
- User: "Hàng bị vỡ" -> Tạo ticket "High Priority"

---

### 📍 PHASE 4: Analytics & Finalization (Tuần 7-8)

**Mục tiêu**: Text-to-SQL + Hoàn thiện

#### Checklist:

- [ ] **4.1 Text-to-SQL**
  ```python
  # ai_modules/nlq/text_to_sql.py
  def generate_sql(question: str, schema: str):
      # Use LLM to generate SQL
  ```

- [ ] **4.2 Analytics API**
  ```python
  # backend/api/v1/endpoints/analytics.py
  @router.post("/query")
  async def nlq_query(question: str):
      # Generate SQL -> Execute -> Return result
  ```

- [ ] **4.3 Agent Playground (Frontend)**
  - Show agent thoughts
  - Debug interface

- [ ] **4.4 Testing & Documentation**
  - Unit tests
  - Integration tests
  - API documentation

**Deliverable**: Admin hỏi "Doanh thu tuần này?" -> Hệ thống trả số liệu.

---

## 💡 Hướng Dẫn Phát Triển

### Chạy Backend (Development)

```bash
cd backend
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Truy cập:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs

### Chạy Frontend (Development)

```bash
cd frontend
npm run dev
```

Truy cập: http://localhost:3000 (React) hoặc http://localhost:5173 (Vite)

### Database Migrations

```bash
cd backend

# Tạo migration mới
alembic revision --autogenerate -m "Add new table"

# Áp dụng migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 📞 Hỗ Trợ & Tài Nguyên

### Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **LangChain**: https://python.langchain.com/docs/
- **ChromaDB**: https://docs.trychroma.com/
- **React**: https://react.dev/
- **SQLAlchemy**: https://docs.sqlalchemy.org/

### Troubleshooting

**Lỗi: ModuleNotFoundError**
```bash
# Đảm bảo virtual environment đã activate
pip install -r requirements.txt
```

**Lỗi: MySQL connection refused**
```bash
# Kiểm tra MySQL đang chạy
# Windows: Task Manager > Services > MySQL
# Hoặc dùng Docker
docker ps | grep mysql
```

**Lỗi: OpenAI API rate limit**
- Dùng API key có quota
- Hoặc switch sang Gemini (miễn phí hơn)

---

## ✅ Next Steps

1. **Ngay bây giờ**: Chạy `docker-compose up -d` để test môi trường
2. **Tuần 1**: Bắt đầu Phase 1 - Database & Backend CRUD
3. **Follow roadmap**: Làm từng Phase một cách tuần tự

Good luck! 🚀
