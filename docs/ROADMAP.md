# 📊 ROADMAP CHI TIẾT - CRM-AI-AGENT

## Tổng Quan Lộ Trình 8 Tuần

| Tuần | Phase | Trọng Tâm | Deliverables |
|------|-------|-----------|--------------|
| 1-2  | Phase 1 | Core Foundation | Backend CRUD + Frontend cơ bản |
| 3-4  | Phase 2 | RAG System | Chatbot FAQ với Knowledge Base |
| 5-6  | Phase 3 | AI Agent | Agent thực hiện hành động |
| 7-8  | Phase 4 | Analytics & Finalization | Text-to-SQL + Demo |

---

## 📅 PHASE 1: CORE FOUNDATION (Tuần 1-2)

### Week 1: Database & Backend API

#### Day 1-2: Database Setup
- [ ] Thiết kế Schema MySQL dựa trên ERD
- [ ] Tạo file `database/schemas/init.sql`
- [ ] Setup Alembic cho migrations
- [ ] Test connection với MySQL

**Files cần tạo:**
```
database/schemas/init.sql
backend/database/session.py
backend/alembic.ini
backend/alembic/env.py
```

#### Day 3-4: SQLAlchemy Models
- [ ] `backend/models/user.py`
- [ ] `backend/models/product.py`
- [ ] `backend/models/order.py`
- [ ] `backend/models/ticket.py`
- [ ] `backend/models/kb_article.py`

**Relationships:**
- User 1-N Orders
- Order N-N Products (through OrderItems)
- User 1-N Tickets

#### Day 5-6: Pydantic Schemas & CRUD
- [ ] Schemas cho mỗi model (Create, Update, Response)
- [ ] Service layer cho business logic
- [ ] CRUD operations

#### Day 7: Authentication
- [ ] JWT token generation
- [ ] Password hashing (bcrypt)
- [ ] Login/Register endpoints

**Test:**
```bash
# Postman/Thunder Client
POST /api/v1/auth/register
POST /api/v1/auth/login
GET /api/v1/products (with Bearer token)
```

### Week 2: Frontend & Integration

#### Day 1-2: Frontend Setup
- [ ] Initialize React/Vue project
- [ ] Setup Axios for API calls
- [ ] Setup routing (React Router/Vue Router)
- [ ] Create layout structure

#### Day 3-4: Core Components
- [ ] Login/Register forms
- [ ] Dashboard layout
- [ ] Product listing
- [ ] Order management

#### Day 5: Seed Data
- [ ] Script tạo 100 products
- [ ] Script tạo 1000 orders
- [ ] Script tạo users với roles khác nhau

**Run:**
```bash
python database/seeds/fake_data.py
```

#### Day 6-7: Testing & Bug Fixes
- [ ] Integration testing
- [ ] Fix bugs
- [ ] Code cleanup

**Deliverable Week 2:**
- Video demo: Login -> Xem products -> Tạo order

---

## 📅 PHASE 2: RAG SYSTEM (Tuần 3-4)

### Week 3: Document Processing Pipeline

#### Day 1-2: Vector Store Setup
- [ ] ChromaDB initialization
- [ ] Collection management
- [ ] Test embedding storage

**File:**
```python
# ai_modules/vector_store/chroma_store.py
class ChromaVectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(...)
    
    def add_documents(self, texts, metadatas):
        pass
    
    def search(self, query, top_k=5):
        pass
```

#### Day 3-4: Document Loaders
- [ ] PDF Loader (LangChain)
- [ ] DOCX Loader
- [ ] TXT/MD Loader

**File:**
```python
# ai_modules/rag_pipeline/loaders/document_loader.py
def load_pdf(file_path):
    loader = PyPDFLoader(file_path)
    return loader.load()
```

#### Day 5-6: Chunking & Embedding
- [ ] RecursiveCharacterTextSplitter
- [ ] OpenAI Embeddings integration
- [ ] Batch processing

**Parameters:**
```python
chunk_size = 1000
chunk_overlap = 200
```

#### Day 7: Knowledge Base API
- [ ] Upload endpoint
- [ ] List articles endpoint
- [ ] Delete article endpoint

**Endpoints:**
```
POST /api/v1/kb/upload
GET /api/v1/kb/articles
DELETE /api/v1/kb/articles/{id}
```

### Week 4: RAG Chat Implementation

#### Day 1-2: Retrieval Logic
- [ ] Similarity search
- [ ] Re-ranking (optional)
- [ ] Context assembly

**Flow:**
```
User Query -> Embed -> Search Vector DB -> Top K chunks
```

#### Day 3-4: LLM Integration
- [ ] OpenAI ChatCompletion API
- [ ] Prompt engineering
- [ ] Source citation

**Prompt Template:**
```
Context:
{retrieved_chunks}

Question: {user_question}

Answer based on the context above. Cite sources.
```

#### Day 5: Chat API
- [ ] `/api/v1/chat` endpoint
- [ ] Conversation history (optional)
- [ ] Streaming response (optional)

#### Day 6-7: Chat Widget (Frontend)
- [ ] Floating chat button
- [ ] Chat interface
- [ ] Message display with citations

**Deliverable Week 4:**
- Video demo: Upload PDF -> Chat hỏi -> Bot trả lời có nguồn

---

## 📅 PHASE 3: AI AGENT (Tuần 5-6)

### Week 5: Tool Definition & Agent Logic

#### Day 1-2: Function Calling Tools
- [ ] `lookup_order(order_id)`: Tra cứu đơn hàng
- [ ] `cancel_order(order_id)`: Hủy đơn
- [ ] `search_products(query)`: Tìm sản phẩm
- [ ] `create_ticket(description)`: Tạo ticket

**File:**
```python
# ai_modules/agents/tools/order_tools.py
def lookup_order(order_id: str) -> dict:
    """Lookup order status by ID"""
    # Query database
    return {"order_id": order_id, "status": "shipped"}
```

#### Day 3-4: LangGraph Workflow
- [ ] Define agent states
- [ ] Create decision nodes
- [ ] Route between RAG and Tools

**Graph:**
```
START -> Classify Intent -> RAG/Tool -> Response -> END
```

#### Day 5-6: Sentiment Analysis
- [ ] TextBlob integration
- [ ] Save sentiment to Ticket
- [ ] Auto-priority based on sentiment

**Logic:**
```python
if sentiment_score < -0.5:
    ticket.priority = "High"
```

#### Day 7: Testing
- [ ] Test all tools
- [ ] Test agent routing
- [ ] Test edge cases

### Week 6: Smart Features & UI

#### Day 1-2: Smart Ticket Routing
- [ ] Auto-tag tickets (Complaint, Question, Request)
- [ ] Assign to staff based on rules
- [ ] Email notifications (optional)

#### Day 3-4: Product Recommendation
- [ ] Semantic search products
- [ ] "Find me X under Y price"

#### Day 5-6: Agent Debugging UI
- [ ] Show agent thoughts
- [ ] Show tools called
- [ ] Show retrieved context

**Frontend Component:**
```jsx
<AgentPlayground>
  <AgentThoughts />
  <ToolCalls />
  <ContextViewer />
</AgentPlayground>
```

#### Day 7: Integration & Testing

**Deliverable Week 6:**
- Video demo:
  - User: "Hủy đơn #123" -> Agent hủy
  - User: "Tìm giày dưới 1 triệu" -> Agent gợi ý

---

## 📅 PHASE 4: ANALYTICS & FINALIZATION (Tuần 7-8)

### Week 7: Text-to-SQL & Dashboard

#### Day 1-3: Text-to-SQL Agent
- [ ] Provide DB schema to LLM
- [ ] Generate SQL from natural language
- [ ] Execute safely (read-only user)
- [ ] Return results

**File:**
```python
# ai_modules/nlq/text_to_sql.py
def generate_sql(question: str, schema: dict) -> str:
    prompt = f"""
    Given this schema: {schema}
    Generate MySQL query for: {question}
    """
    sql = llm.invoke(prompt)
    return sql
```

**Examples:**
- "Doanh thu tuần này?" -> `SELECT SUM(total) FROM orders WHERE ...`
- "Top 3 sản phẩm bán chạy?" -> `SELECT product_id, COUNT(*) FROM order_items ...`

#### Day 4-5: Analytics Dashboard
- [ ] Chart visualization (Chart.js/Recharts)
- [ ] Natural language query box
- [ ] Display SQL + Results

#### Day 6-7: Testing
- [ ] Test complex queries
- [ ] Edge cases handling
- [ ] Security (SQL injection prevention)

### Week 8: Finalization & Demo

#### Day 1-2: Testing Comprehensive
- [ ] Unit tests (Pytest)
- [ ] Integration tests
- [ ] Fix bugs

#### Day 3-4: Documentation
- [ ] Update README
- [ ] API documentation
- [ ] Deployment guide

#### Day 5: Demo Preparation
- [ ] Prepare demo script
- [ ] Create demo data
- [ ] Test demo flow

**Demo Scenarios:**
1. **RAG**: Upload chính sách -> Hỏi FAQ
2. **Agent**: Tra cứu đơn, hủy đơn
3. **Sentiment**: Chat tiêu cực -> Auto high priority ticket
4. **NLQ**: Admin hỏi số liệu -> Trả kết quả

#### Day 6-7: Video Recording & Submission
- [ ] Record demo video (10-15 phút)
- [ ] Create presentation slides
- [ ] Final code cleanup
- [ ] Submit

---

## 🎯 Checklist Tính Năng Bắt Buộc (Must-Have)

### Core Features ✅
- [x] Authentication (JWT)
- [ ] Product CRUD
- [ ] Order CRUD
- [ ] Ticket System

### AI Features (Trọng Điểm) 🤖
- [ ] **RAG FAQ**: Upload PDF -> Chat FAQ
- [ ] **AI Agent Tool Use**: Tra cứu/Hủy đơn
- [ ] **Sentiment Analysis**: Phân loại cảm xúc
- [ ] **NLQ**: Hỏi số liệu bằng ngôn ngữ tự nhiên

### Nice-to-Have (Optional) ⭐
- [ ] Conversation history
- [ ] Multi-language support
- [ ] Telegram/Messenger integration
- [ ] Real-time notifications

---

## 📈 Tiêu Chí Đánh Giá (Dự Kiến)

| Tiêu Chí | Trọng Số | Mô Tả |
|----------|----------|-------|
| **Chức năng cơ bản** | 20% | CRUD hoạt động tốt |
| **RAG System** | 25% | Chatbot trả lời FAQ chính xác |
| **AI Agent** | 30% | Agent thực hiện hành động đúng |
| **NLQ Analytics** | 15% | Text-to-SQL hoạt động |
| **UI/UX** | 5% | Giao diện dễ dùng |
| **Documentation** | 5% | Tài liệu đầy đủ |

---

## 💪 Tips Để Thành Công

1. **Commit thường xuyên**: Mỗi ngày ít nhất 1 commit
2. **Test sớm**: Đừng đợi đến cuối mới test
3. **Focus on AI**: Đây là điểm nhấn của dự án
4. **Document as you go**: Viết docs ngay khi code
5. **Ask for help**: Tham khảo docs, Stack Overflow, ChatGPT

---

**Good luck! Chúc bạn hoàn thành xuất sắc dự án! 🚀**
