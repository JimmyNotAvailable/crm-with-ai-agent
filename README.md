# CRM-AI-Agent 🤖

**Hệ thống CRM thế hệ mới tích hợp AI Agent & RAG** - Đồ án môn học CS434

## 📋 Tổng Quan Dự Án

Xây dựng hệ thống CRM (Customer Relationship Management) thông minh tích hợp các công nghệ AI tiên tiến:

- **RAG (Retrieval-Augmented Generation)**: Trả lời FAQ tự động từ Knowledge Base
- **AI Agent với Tool Use**: Thực hiện hành động nghiệp vụ (tra cứu đơn hàng, hủy đơn, gợi ý sản phẩm)
- **NLQ (Natural Language Querying)**: Hỏi đáp số liệu bằng ngôn ngữ tự nhiên (Text-to-SQL)
- **Sentiment Analysis**: Phân tích cảm xúc khách hàng tự động

## 🏗️ Kiến Trúc Hệ Thống

```
CRM-AI-Agent/
├── backend/                 # FastAPI Backend
│   ├── api/                # API Endpoints
│   │   └── v1/
│   │       └── endpoints/  # Auth, Products, Orders, Chat, etc.
│   ├── core/               # Config, Security, Dependencies
│   ├── models/             # SQLAlchemy Models (MySQL)
│   ├── schemas/            # Pydantic Schemas
│   ├── services/           # Business Logic
│   ├── database/           # DB Connection
│   └── utils/              # Helper Functions
│
├── frontend/               # React/Vue Frontend
│   ├── public/
│   └── src/
│       ├── components/     # UI Components
│       │   ├── chat/       # Chat Widget
│       │   ├── dashboard/  # Admin Dashboard
│       │   └── common/     # Shared Components
│       ├── pages/          # Page Views
│       ├── services/       # API Services
│       ├── store/          # State Management
│       └── utils/
│
├── ai_modules/             # AI Core Logic
│   ├── rag_pipeline/       # RAG System
│   │   ├── loaders/        # Document Loaders (PDF, Docx)
│   │   ├── chunking/       # Text Splitting
│   │   ├── embeddings/     # Vector Embeddings
│   │   └── retrieval/      # Similarity Search
│   ├── agents/             # AI Agent System
│   │   ├── tools/          # Function Calling Tools
│   │   └── workflows/      # Agent Logic (LangGraph)
│   ├── nlq/                # Natural Language Query (Text-to-SQL)
│   ├── sentiment/          # Sentiment Analysis
│   └── vector_store/       # ChromaDB/Vector DB
│
├── database/
│   ├── migrations/         # Alembic Migrations
│   ├── seeds/              # Seed Data Scripts
│   ├── schemas/            # SQL Schema Files
│   └── scripts/            # Utility Scripts
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── docs/                   # Documentation
├── uploads/                # User Uploaded Files
├── logs/                   # Application Logs
├── requirements.txt        # Python Dependencies
├── .env.example            # Environment Variables Template
├── docker-compose.yml      # Docker Setup
└── README.md              # This file
```

## 🚀 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: MySQL 8.0
- **Vector DB**: ChromaDB
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic

### AI/ML
- **LLM Framework**: LangChain, LangGraph
- **LLM Provider**: OpenAI GPT-4 (hoặc Gemini, Claude)
- **Embeddings**: OpenAI Embeddings / Sentence Transformers
- **Document Processing**: PyPDF, python-docx
- **NLP**: TextBlob, Transformers

### Frontend
- **Framework**: React 18 / Vue 3
- **State Management**: Redux / Pinia
- **HTTP Client**: Axios
- **UI Library**: TailwindCSS / Material-UI

### DevOps
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest

## 📦 Cài Đặt & Chạy Dự Án

### 1. Clone Repository

```bash
git clone <repository-url>
cd CRM-AI-Agent
```

### 2. Cấu Hình Environment

```bash
# Copy file .env.example thành .env
cp .env.example .env

# Chỉnh sửa .env với thông tin của bạn
# Quan trọng nhất: OPENAI_API_KEY, MYSQL_PASSWORD
```

### 3. Chạy với Docker (Khuyến nghị)

```bash
# Khởi động tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f

# Truy cập:
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:3000
# - API Docs: http://localhost:8000/docs
```

### 4. Hoặc Chạy Manual (Development)

#### Backend

```bash
cd backend

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Cài đặt dependencies
pip install -r ../requirements.txt

# Chạy migrations
alembic upgrade head

# Chạy server
uvicorn main:app --reload
```

#### Frontend

```bash
cd frontend

# Cài đặt dependencies
npm install

# Chạy dev server
npm run dev
```

### 5. Seed Data (Optional)

```bash
# Tạo dữ liệu mẫu (100 products, 1000 orders)
python database/seeds/fake_data.py
```

## 🎯 Các Tính Năng Chính

### Phase 1: Core Foundation (Tuần 1-2) ✅
- [x] Thiết kế Database Schema (MySQL)
- [x] Backend API CRUD (Users, Products, Orders, Tickets)
- [x] Authentication (JWT)
- [x] Basic Frontend UI (Dashboard, Product List)

### Phase 2: RAG System (Tuần 3-4) 🚧
- [ ] Document Ingestion Pipeline (Upload PDF/Docx)
- [ ] Text Chunking & Embedding
- [ ] Vector Storage (ChromaDB)
- [ ] RAG Chat API với Source Citation

### Phase 3: AI Agent (Tuần 5-6) 📋
- [ ] Function Calling Tools (lookup_order, cancel_order, recommend_product)
- [ ] Agentic Workflow (LangGraph)
- [ ] Sentiment Analysis Integration
- [ ] Smart Ticket Routing

### Phase 4: Analytics & Finalization (Tuần 7-8) 📋
- [ ] Text-to-SQL Agent (NLQ Dashboard)
- [ ] Agent Debugging Playground
- [ ] Testing & Documentation
- [ ] Video Demo

## 📚 API Documentation

Sau khi chạy backend, truy cập:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Các Endpoints Chính

```
POST   /api/v1/auth/register          # Đăng ký
POST   /api/v1/auth/login             # Đăng nhập
GET    /api/v1/products               # Danh sách sản phẩm
POST   /api/v1/orders                 # Tạo đơn hàng
GET    /api/v1/orders/{id}            # Chi tiết đơn hàng
POST   /api/v1/chat                   # Chat với AI Agent
POST   /api/v1/kb/upload              # Upload tài liệu Knowledge Base
POST   /api/v1/analytics/query        # NLQ Query
```

## 🧪 Testing

```bash
# Chạy tất cả tests
pytest

# Chạy với coverage
pytest --cov=backend --cov-report=html

# Chạy specific test
pytest tests/unit/test_rag_pipeline.py
```

## 🤝 Contributing

Dự án này là đồ án môn học. Nếu bạn muốn đóng góp:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

MIT License - Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## 👥 Team

- **Sinh viên thực hiện**: [Tên của bạn]
- **MSSV**: [Mã số sinh viên]
- **Lớp**: CS434
- **Giảng viên hướng dẫn**: [Tên giảng viên]

## 📞 Liên Hệ

- Email: [email@example.com]
- GitHub: [github.com/username]

---

**Note**: Đây là dự án đồ án môn học, không dùng cho mục đích thương mại.
