# 🎯 CHIA CÔNG VIỆC THEO PHASE

## 📋 TỔNG QUAN PHÂN CÔNG

Dự án được chia thành **4 Phases chính** trong **8 tuần**. Dưới đây là checklist chi tiết cho từng phase.

---

## 🗓️ PHASE 1: CORE FOUNDATION (Tuần 1-2)

### 📍 Mục Tiêu
Xây dựng hệ thống Backend + Frontend cơ bản với đầy đủ chức năng CRUD.

### ✅ Checklist Chi Tiết

#### Week 1: Database & Backend Setup

##### Day 1: Environment Setup
- [ ] Copy `.env.example` thành `.env`
- [ ] Điền OpenAI API Key vào `.env`
- [ ] Chạy `docker-compose up -d` để test
- [ ] Verify MySQL đang chạy: `docker ps | findstr mysql`
- [ ] Verify Backend đang chạy: Visit http://localhost:8000/docs

##### Day 2: Database Schema Design
- [ ] Phân tích ERD từ file `database_CRM.drawio`
- [ ] Tạo file `database/schemas/init.sql` với:
  - [ ] Table `users` (id, email, password_hash, role, created_at)
  - [ ] Table `products` (id, name, description, price, stock)
  - [ ] Table `categories` (id, name)
  - [ ] Table `orders` (id, user_id, status, total, created_at)
  - [ ] Table `order_items` (id, order_id, product_id, quantity, price)
  - [ ] Table `tickets` (id, user_id, subject, status, priority)
  - [ ] Table `messages` (id, ticket_id, sender_id, content)
  - [ ] Table `kb_articles` (id, title, file_path, created_at)

##### Day 3: Alembic Setup
- [ ] `cd backend`
- [ ] `alembic init alembic`
- [ ] Chỉnh sửa `alembic.ini`: Set `sqlalchemy.url`
- [ ] Chỉnh sửa `alembic/env.py`: Import models
- [ ] Test: `alembic revision --autogenerate -m "Test"`

##### Day 4-5: SQLAlchemy Models
- [ ] `backend/models/user.py`:
  ```python
  class User(Base):
      __tablename__ = "users"
      id = Column(Integer, primary_key=True)
      email = Column(String(255), unique=True)
      password_hash = Column(String(255))
      role = Column(Enum("admin", "staff", "customer"))
  ```
- [ ] `backend/models/product.py`: Product model
- [ ] `backend/models/order.py`: Order + OrderItem models
- [ ] `backend/models/ticket.py`: Ticket + Message models
- [ ] `backend/models/kb_article.py`: KBArticle model
- [ ] `backend/database/session.py`: Session management

##### Day 6: Database Migration
- [ ] `alembic revision --autogenerate -m "Initial schema"`
- [ ] Review migration file
- [ ] `alembic upgrade head`
- [ ] Verify tables created: Connect to MySQL and run `SHOW TABLES;`

##### Day 7: Authentication & Security
- [ ] `backend/core/security.py`:
  - [ ] `hash_password(password: str) -> str`
  - [ ] `verify_password(plain, hashed) -> bool`
  - [ ] `create_access_token(data: dict) -> str`
  - [ ] `decode_access_token(token: str) -> dict`
- [ ] Test hashing: `bcrypt.hashpw()`
- [ ] Test JWT: `jose.jwt.encode()`

#### Week 2: API Endpoints & Frontend

##### Day 1: Pydantic Schemas
- [ ] `backend/schemas/user.py`:
  - [ ] `UserCreate`, `UserLogin`, `UserResponse`, `Token`
- [ ] `backend/schemas/product.py`:
  - [ ] `ProductCreate`, `ProductUpdate`, `ProductResponse`
- [ ] `backend/schemas/order.py`:
  - [ ] `OrderCreate`, `OrderItemCreate`, `OrderResponse`

##### Day 2: Authentication API
- [ ] `backend/api/v1/endpoints/auth.py`:
  - [ ] `POST /register`: Create user
  - [ ] `POST /login`: Return JWT token
  - [ ] `GET /me`: Get current user info
- [ ] Test với Swagger UI (http://localhost:8000/docs)

##### Day 3: Product & Order APIs
- [ ] `backend/api/v1/endpoints/products.py`:
  - [ ] `GET /products`: List all (with pagination)
  - [ ] `GET /products/{id}`: Get one
  - [ ] `POST /products`: Create (Admin only)
  - [ ] `PUT /products/{id}`: Update (Admin only)
  - [ ] `DELETE /products/{id}`: Delete (Admin only)
- [ ] `backend/api/v1/endpoints/orders.py`:
  - [ ] `POST /orders`: Create order
  - [ ] `GET /orders`: List user's orders
  - [ ] `GET /orders/{id}`: Get order detail

##### Day 4: Seed Data Script
- [ ] `database/seeds/fake_data.py`:
  ```python
  from faker import Faker
  # Generate 100 products
  # Generate 50 users
  # Generate 1000 orders
  ```
- [ ] Run: `python database/seeds/fake_data.py`
- [ ] Verify: Query database to check data

##### Day 5-6: Frontend Setup
- [ ] `cd frontend`
- [ ] Initialize React: `npm create vite@latest . -- --template react`
- [ ] Install dependencies: `npm install axios react-router-dom zustand`
- [ ] Install TailwindCSS: `npm install -D tailwindcss postcss autoprefixer`
- [ ] Setup Tailwind config
- [ ] Create folder structure (already done)
- [ ] `src/services/api.js`: Axios instance with interceptors
- [ ] `src/store/authStore.js`: Auth state (Zustand)

##### Day 7: Frontend Components
- [ ] `src/pages/Login.jsx`: Login form
- [ ] `src/pages/Dashboard.jsx`: Main dashboard
- [ ] `src/pages/Products.jsx`: Product listing
- [ ] `src/components/common/Navbar.jsx`: Navigation
- [ ] Connect to Backend API
- [ ] Test full flow: Login -> Dashboard -> Products

### 📦 Deliverables Phase 1
- [x] Database schema với 8+ tables
- [x] Backend API với 10+ endpoints
- [x] JWT Authentication hoạt động
- [x] 100 products, 1000 orders fake data
- [x] Frontend cơ bản với Login, Dashboard, Products
- [x] Video demo: Login -> View products -> Create order

---

## 🗓️ PHASE 2: RAG SYSTEM (Tuần 3-4)

### 📍 Mục Tiêu
Xây dựng hệ thống RAG để Chatbot trả lời FAQ từ tài liệu.

### ✅ Checklist Chi Tiết

#### Week 3: Document Processing Pipeline

##### Day 1: ChromaDB Setup
- [ ] `ai_modules/vector_store/chroma_store.py`:
  ```python
  import chromadb
  client = chromadb.PersistentClient(path="./chroma_db")
  collection = client.get_or_create_collection("kb_articles")
  ```
- [ ] Test: Add sample document, query it

##### Day 2: Document Loaders
- [ ] `ai_modules/rag_pipeline/loaders/pdf_loader.py`:
  ```python
  from langchain.document_loaders import PyPDFLoader
  def load_pdf(file_path):
      loader = PyPDFLoader(file_path)
      return loader.load()
  ```
- [ ] `ai_modules/rag_pipeline/loaders/docx_loader.py`: DOCX loader
- [ ] Test: Load sample PDF, print pages

##### Day 3: Text Chunking
- [ ] `ai_modules/rag_pipeline/chunking/text_splitter.py`:
  ```python
  from langchain.text_splitter import RecursiveCharacterTextSplitter
  splitter = RecursiveCharacterTextSplitter(
      chunk_size=1000,
      chunk_overlap=200
  )
  ```
- [ ] Test: Split sample text, verify chunks

##### Day 4: Embeddings
- [ ] `ai_modules/rag_pipeline/embeddings/embedding_service.py`:
  ```python
  from langchain.embeddings import OpenAIEmbeddings
  embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
  ```
- [ ] Test: Embed sample text, verify vector dimensions

##### Day 5: Ingestion Pipeline
- [ ] Combine: Load -> Chunk -> Embed -> Store
- [ ] `ai_modules/rag_pipeline/ingestion.py`:
  ```python
  def ingest_document(file_path):
      docs = load_pdf(file_path)
      chunks = split_text(docs)
      embeddings = embed_chunks(chunks)
      store_in_chroma(embeddings)
  ```

##### Day 6: Knowledge Base API - Upload
- [ ] `backend/api/v1/endpoints/kb.py`:
  - [ ] `POST /kb/upload`: 
    - Save file to `uploads/`
    - Call ingestion pipeline
    - Save metadata to `kb_articles` table
- [ ] Test upload: PDF file -> ChromaDB

##### Day 7: Knowledge Base API - List & Delete
- [ ] `GET /kb/articles`: List all uploaded documents
- [ ] `DELETE /kb/articles/{id}`: Delete document + vectors

#### Week 4: RAG Chat Implementation

##### Day 1: Retrieval Logic
- [ ] `ai_modules/rag_pipeline/retrieval/retriever.py`:
  ```python
  def retrieve_context(query: str, top_k=5):
      query_vector = embeddings.embed_query(query)
      results = collection.query(query_vector, n_results=top_k)
      return results
  ```

##### Day 2: Prompt Engineering
- [ ] Create prompt template:
  ```python
  PROMPT = """
  You are a helpful customer service assistant.
  
  Context from knowledge base:
  {context}
  
  User question: {question}
  
  Answer based on the context above. If you don't know, say so.
  Cite your sources like [Source: filename.pdf, page X].
  """
  ```

##### Day 3: LLM Integration
- [ ] `ai_modules/rag_pipeline/generator.py`:
  ```python
  from openai import OpenAI
  client = OpenAI(api_key=settings.OPENAI_API_KEY)
  
  def generate_answer(context, question):
      response = client.chat.completions.create(
          model="gpt-4-turbo-preview",
          messages=[...]
      )
      return response
  ```

##### Day 4: Chat API
- [ ] `backend/api/v1/endpoints/chat.py`:
  - [ ] `POST /chat`:
    - Receive user message
    - Retrieve context from ChromaDB
    - Generate answer with LLM
    - Return answer with citations
- [ ] Test: Send question -> Get answer

##### Day 5: Chat Widget (Frontend)
- [ ] `src/components/chat/ChatWidget.jsx`: Floating button
- [ ] `src/components/chat/ChatWindow.jsx`: Chat interface
- [ ] `src/components/chat/MessageList.jsx`: Display messages
- [ ] `src/components/chat/MessageInput.jsx`: Input box

##### Day 6: Chat Integration
- [ ] Connect ChatWidget to Backend `/chat` API
- [ ] Display messages with citations
- [ ] Add typing indicator
- [ ] Add error handling

##### Day 7: Testing & Demo
- [ ] Upload sample PDF (e.g., return policy)
- [ ] Test questions:
  - "What is the return policy?"
  - "Can I return after 30 days?"
  - "How do I get a refund?"
- [ ] Verify citations are shown
- [ ] Record demo video

### 📦 Deliverables Phase 2
- [x] Document upload working (PDF, DOCX)
- [x] Text chunking & embedding pipeline
- [x] ChromaDB vector storage
- [x] RAG Chat API functional
- [x] Chat widget on Frontend
- [x] Video demo: Upload PDF -> Ask FAQ -> Bot answers with sources

---

## 🗓️ PHASE 3: AI AGENT (Tuần 5-6)

### 📍 Mục Tiêu
Nâng cấp Chatbot thành AI Agent có khả năng thực hiện hành động.

### ✅ Checklist Chi Tiết

#### Week 5: Agent Tools & Workflow

##### Day 1: Define Order Tools
- [ ] `ai_modules/agents/tools/order_tools.py`:
  ```python
  def lookup_order(order_id: str) -> dict:
      """Lookup order by ID"""
      # Query database
      
  def cancel_order(order_id: str) -> dict:
      """Cancel order if eligible"""
      # Update order status
      
  def get_order_tracking(order_id: str) -> dict:
      """Get shipping status"""
      # Return tracking info
  ```

##### Day 2: Define Product Tools
- [ ] `ai_modules/agents/tools/product_tools.py`:
  ```python
  def search_products(query: str, max_price: float = None) -> list:
      """Search products by keyword and price"""
      # Semantic search in database
      
  def recommend_products(category: str) -> list:
      """Recommend products in category"""
      # Return top rated products
  ```

##### Day 3: Define Ticket Tools
- [ ] `ai_modules/agents/tools/ticket_tools.py`:
  ```python
  def create_ticket(user_id: int, subject: str, description: str, priority: str) -> dict:
      """Create support ticket"""
      # Insert into tickets table
      
  def update_ticket_priority(ticket_id: int, priority: str) -> dict:
      """Update ticket priority"""
      # Update priority field
  ```

##### Day 4: LangGraph Workflow Setup
- [ ] `ai_modules/agents/workflows/agent_graph.py`:
  ```python
  from langgraph.graph import StateGraph
  
  # Define states
  class AgentState(TypedDict):
      messages: list
      intent: str
      result: str
  
  # Define nodes
  def classify_intent(state): ...
  def rag_node(state): ...
  def tool_node(state): ...
  
  # Build graph
  graph = StateGraph(AgentState)
  graph.add_node("classify", classify_intent)
  graph.add_node("rag", rag_node)
  graph.add_node("tools", tool_node)
  ```

##### Day 5: Agent Routing Logic
- [ ] Implement intent classification:
  - "FAQ" -> Route to RAG
  - "Order inquiry" -> Route to order_tools
  - "Product search" -> Route to product_tools
  - "Complaint" -> Route to ticket_tools + sentiment analysis

##### Day 6: Sentiment Analysis
- [ ] `ai_modules/sentiment/analyzer.py`:
  ```python
  from textblob import TextBlob
  
  def analyze_sentiment(text: str) -> dict:
      blob = TextBlob(text)
      polarity = blob.sentiment.polarity
      
      if polarity < -0.3:
          label = "negative"
      elif polarity > 0.3:
          label = "positive"
      else:
          label = "neutral"
      
      return {"score": polarity, "label": label}
  ```

##### Day 7: Smart Ticket Routing
- [ ] Auto-detect negative sentiment -> Create High Priority ticket
- [ ] Auto-tag tickets (Complaint, Question, Request)
- [ ] Test: Send angry message -> Verify High Priority ticket created

#### Week 6: Agent Integration & UI

##### Day 1-2: Agent Main Orchestrator
- [ ] `ai_modules/agents/agent.py`:
  ```python
  class CustomerServiceAgent:
      def __init__(self):
          self.graph = build_agent_graph()
          self.tools = load_tools()
      
      def run(self, user_message: str, user_id: int):
          # Run agent graph
          # Return response
  ```

##### Day 3: Update Chat API
- [ ] Modify `backend/api/v1/endpoints/chat.py`:
  - Replace simple RAG with Agent
  - Agent decides: RAG or Tool use

##### Day 4: Product Recommendation
- [ ] Test: "Find me running shoes under $100"
- [ ] Verify: Agent calls `search_products()` tool
- [ ] Verify: Returns product list

##### Day 5: Order Actions
- [ ] Test: "What's the status of order #123?"
- [ ] Test: "Cancel order #123"
- [ ] Verify: Agent calls correct tool

##### Day 6: Agent Playground (Frontend)
- [ ] `src/pages/AgentPlayground.jsx`:
  - Show user message
  - Show agent thoughts (which node executed)
  - Show tools called with parameters
  - Show retrieved context (if RAG)
  - Show final response

##### Day 7: Testing & Demo
- [ ] Test all scenarios:
  - FAQ question
  - Order lookup
  - Product search
  - Complaint (negative sentiment)
- [ ] Record demo video

### 📦 Deliverables Phase 3
- [x] Function calling tools (6+ tools)
- [x] LangGraph agent workflow
- [x] Sentiment analysis integration
- [x] Smart ticket routing
- [x] Agent playground UI
- [x] Video demo: Multiple agent scenarios

---

## 🗓️ PHASE 4: ANALYTICS & FINALIZATION (Tuần 7-8)

### 📍 Mục Tiêu
Text-to-SQL Analytics + Hoàn thiện dự án

### ✅ Checklist Chi Tiết

#### Week 7: NLQ Analytics

##### Day 1: Database Schema for LLM
- [ ] `ai_modules/nlq/schema_provider.py`:
  ```python
  def get_database_schema() -> str:
      schema = """
      Table: orders
      - id: INT (Primary Key)
      - user_id: INT (Foreign Key to users)
      - total: DECIMAL
      - status: VARCHAR (pending, shipped, delivered)
      - created_at: DATETIME
      
      Table: order_items
      - order_id: INT
      - product_id: INT
      - quantity: INT
      - price: DECIMAL
      
      ...
      """
      return schema
  ```

##### Day 2: Text-to-SQL Generator
- [ ] `ai_modules/nlq/text_to_sql.py`:
  ```python
  def generate_sql(question: str, schema: str) -> str:
      prompt = f"""
      Given this database schema:
      {schema}
      
      Generate a MySQL query for: {question}
      
      Return ONLY the SQL query, no explanation.
      """
      
      response = llm.invoke(prompt)
      return extract_sql(response)
  ```

##### Day 3: Safe SQL Execution
- [ ] Create read-only MySQL user
- [ ] `ai_modules/nlq/executor.py`:
  ```python
  def execute_sql_safely(sql: str):
      # Validate SQL (no INSERT, UPDATE, DELETE)
      if not is_safe_sql(sql):
          raise SecurityError("Unsafe SQL")
      
      # Execute with read-only connection
      result = db.execute(sql)
      return result
  ```

##### Day 4: Analytics API
- [ ] `backend/api/v1/endpoints/analytics.py`:
  - [ ] `POST /analytics/query`:
    - Receive natural language question
    - Generate SQL
    - Execute SQL
    - Return results + SQL query

##### Day 5: Test Queries
- [ ] "What is the total revenue this week?"
- [ ] "Top 5 best-selling products this month"
- [ ] "How many orders are pending?"
- [ ] "Average order value by day"

##### Day 6: Analytics Dashboard (Frontend)
- [ ] `src/pages/Analytics.jsx`:
  - Natural language input box
  - Display generated SQL
  - Display results (table/chart)
  - Chart.js/Recharts for visualization

##### Day 7: Chart Visualization
- [ ] Bar chart for product sales
- [ ] Line chart for revenue over time
- [ ] Pie chart for order status distribution

#### Week 8: Finalization & Demo

##### Day 1: Unit Testing
- [ ] `tests/unit/test_auth.py`: Auth service tests
- [ ] `tests/unit/test_rag_pipeline.py`: RAG tests
- [ ] `tests/unit/test_agent.py`: Agent tests
- [ ] Run: `pytest tests/unit/`

##### Day 2: Integration Testing
- [ ] `tests/integration/test_api_auth.py`: Auth API tests
- [ ] `tests/integration/test_api_chat.py`: Chat API tests
- [ ] `tests/integration/test_agent_workflow.py`: End-to-end agent tests
- [ ] Run: `pytest tests/integration/`

##### Day 3: Bug Fixes
- [ ] Fix all failing tests
- [ ] Fix UI bugs
- [ ] Fix edge cases

##### Day 4: Documentation Update
- [ ] Update README.md
- [ ] Write API documentation (`docs/API.md`)
- [ ] Write deployment guide (`docs/DEPLOYMENT.md`)
- [ ] Add inline code comments

##### Day 5: Demo Preparation
- [ ] Prepare demo data (clean fake data)
- [ ] Write demo script
- [ ] Prepare slides (10-15 slides)
- [ ] Test demo flow 3 times

##### Day 6: Video Recording
- [ ] Record demo video (10-15 minutes):
  - Intro: Project overview (1 min)
  - Phase 1: CRUD demo (2 min)
  - Phase 2: RAG demo (3 min)
  - Phase 3: Agent demo (4 min)
  - Phase 4: NLQ demo (2 min)
  - Conclusion: Tech stack, lessons learned (1-2 min)

##### Day 7: Final Submission
- [ ] Code cleanup
- [ ] Final commit
- [ ] Create release tag: `v1.0.0`
- [ ] Submit video
- [ ] Submit code repository link
- [ ] Submit report (if required)

### 📦 Deliverables Phase 4
- [x] Text-to-SQL working for 10+ query types
- [x] Analytics dashboard with charts
- [x] 20+ unit tests passing
- [x] 10+ integration tests passing
- [x] Complete documentation
- [x] Demo video
- [x] Final submission

---

## 📊 Progress Tracking Template

Copy vào file riêng để track progress:

```markdown
# PROGRESS TRACKING

## Phase 1: Core Foundation
- [ ] Week 1 - Database & Backend (0/7 days)
  - [ ] Day 1: Environment Setup
  - [ ] Day 2: Database Schema
  - [ ] Day 3: Alembic Setup
  - [ ] Day 4-5: Models
  - [ ] Day 6: Migration
  - [ ] Day 7: Auth & Security
  
- [ ] Week 2 - API & Frontend (0/7 days)
  - [ ] Day 1: Schemas
  - [ ] Day 2: Auth API
  - [ ] Day 3: Product & Order API
  - [ ] Day 4: Seed Data
  - [ ] Day 5-6: Frontend Setup
  - [ ] Day 7: Frontend Components

## Phase 2: RAG System
- [ ] Week 3 - Document Processing (0/7 days)
- [ ] Week 4 - RAG Chat (0/7 days)

## Phase 3: AI Agent
- [ ] Week 5 - Agent Tools (0/7 days)
- [ ] Week 6 - Agent UI (0/7 days)

## Phase 4: Analytics
- [ ] Week 7 - NLQ (0/7 days)
- [ ] Week 8 - Finalization (0/7 days)
```

---

**Chúc bạn thành công với dự án! 🚀**
