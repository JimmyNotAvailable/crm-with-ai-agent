# PROJECT OVERVIEW: AI-POWERED OMNI-CHANNEL CRM
**Role:** Senior AI Engineer & Business Analyst Mentor
**Scope:** Đồ án tốt nghiệp / Capstone Project (8 Tuần)

---

## 1. TỔNG QUAN DỰ ÁN
Xây dựng hệ thống CRM thế hệ mới tích hợp **AI Agent**, tập trung giải quyết ba bài toán cốt lõi:
1.  **Chăm sóc khách hàng tự động (Customer Service):** Sử dụng RAG (Retrieval-Augmented Generation) để trả lời FAQ.
2.  **Tác vụ thông minh (Agentic Workflow):** AI tự động tra cứu đơn hàng, phân loại ticket và thực hiện hành động (Tool Use).
3.  **Phân tích dữ liệu tự nhiên (NLQ):** Hỏi đáp số liệu kinh doanh bằng ngôn ngữ tự nhiên (Text-to-SQL).

**Tech Stack đề xuất:**
* **Backend:** Python (FastAPI/Flask) - *Bắt buộc để tích hợp LangChain/LlamaIndex.*
* **Database:** MySQL (Nghiệp vụ) + ChromaDB/Milvus (Vector Store).
* **Frontend:** ReactJS/VueJS (Dựa trên cấu trúc UI có sẵn).
* **AI Core:** OpenAI API (hoặc Gemini/Claude), LangChain/LangGraph.

---

## 2. LỘ TRÌNH THỰC HIỆN CHI TIẾT (PHASE-BY-PHASE)

### PHASE 1: CORE FOUNDATION & DATABASE (Tuần 1-2)
**Mục tiêu:** Xây dựng khung sườn hệ thống, hoàn thiện CSDL và các chức năng CRUD cơ bản.

#### Module 1.1: Thiết kế & Khởi tạo Database
* [cite_start]**Phân tích:** Dựa trên file `database_CRM.drawio`[cite: 55], lược bỏ các bảng Marketing phức tạp (`Journey_Nodes`, `Campaign_Sends`) để giảm tải.
* **Thực hiện:**
    1.  [cite_start]Dựng bảng **Users/Auth**: Phân quyền Admin/Staff/Customer[cite: 114, 164].
    2.  [cite_start]Dựng bảng **Products/Inventory**: Quản lý sản phẩm, tồn kho cơ bản[cite: 122, 172].
    3.  [cite_start]Dựng bảng **Orders**: Trọng tâm xử lý trạng thái đơn hàng (`PENDING`, `SHIPPED`...)[cite: 125, 175].
    4.  [cite_start]Dựng bảng **Tickets**: Nơi lưu trữ hội thoại hỗ trợ khách hàng[cite: 130, 180].

#### Module 1.2: Backend API (Core)
* **Thực hiện:**
    1.  Setup FastAPI project structure (Clean Architecture).
    2.  Viết API Authentication (Login/Register - JWT).
    3.  Viết API CRUD cho Product và Order.
    4.  **Simulation Data:** Viết script Python để fake data (100 products, 1000 orders) giúp việc test AI ở Phase sau có dữ liệu thật.

#### Module 1.3: Basic Frontend UI
* [cite_start]**Phân tích:** Dựa trên `CRM_UI_structure.json` [cite: 5] và `demo-ui.html`.
* **Thực hiện:**
    1.  Dựng Layout Dashboard cho Admin/Staff.
    2.  Dựng trang danh sách sản phẩm và chi tiết đơn hàng.
    3.  Tích hợp Chat Widget (Cửa sổ chat) ở góc phải màn hình (quan trọng cho Phase 2).

---

### PHASE 2: INTELLIGENT KNOWLEDGE BASE (RAG) (Tuần 3-4)
[cite_start]**Mục tiêu:** Chatbot có thể trả lời các câu hỏi về chính sách bán hàng, bảo hành dựa trên tài liệu tải lên (Use Case: Tự trả lời FAQ [cite: 1]).

#### Module 2.1: Document Ingestion Pipeline
* **Nhiệm vụ:** Xử lý tài liệu phi cấu trúc (PDF, Docx, MD) thành Vector.
* **Thực hiện:**
    1.  [cite_start]Tạo bảng `KB_Articles` [cite: 144, 194] để quản lý file upload.
    2.  Sử dụng `LangChain` loader để đọc file.
    3.  **Chunking:** Cắt nhỏ văn bản (RecursiveCharacterTextSplitter).
    4.  **Embedding:** Dùng OpenAI Embeddings hoặc HuggingFace (miễn phí) để vector hóa.
    5.  Lưu vào **Vector Database** (ChromaDB/FAISS).

#### Module 2.2: RAG Chat API
* **Nhiệm vụ:** Xử lý luồng chat hỏi đáp.
* **Thực hiện:**
    1.  Nhận câu hỏi từ User -> Convert sang Vector.
    2.  Similarity Search: Tìm 3-5 đoạn văn bản liên quan nhất trong Vector DB.
    3.  **Prompt Engineering:** Gép Context + Question gửi cho LLM.
    4.  Trả về câu trả lời kèm nguồn dẫn (Source citation).

---

### PHASE 3: AI AGENT WORKFLOW (Tuần 5-6)
**Mục tiêu:** Nâng cấp Chatbot thành **Agent** có khả năng hành động, xử lý nghiệp vụ cụ thể thay vì chỉ trả lời lý thuyết.

#### Module 3.1: Tool Definition (Function Calling)
* **Nhiệm vụ:** Dạy cho AI biết hệ thống có những "công cụ" (API) nào.
* **Thực hiện:** Định nghĩa các Python Functions cho Agent:
    1.  `lookup_order(order_id)`: Truy vấn trạng thái đơn hàng từ SQL.
    2.  `cancel_order(order_id)`: Hủy đơn hàng nếu đủ điều kiện.
    3.  `recommend_product(keyword)`: Tìm sản phẩm theo nhu cầu (Semantic Search).

#### Module 3.2: Agentic Logic (ReAct Framework)
* **Nhiệm vụ:** Logic suy luận cho AI.
* **Thực hiện (LangGraph/LangChain):**
    1.  Xây dựng luồng (Graph):
        * User hỏi -> LLM phân loại ý định (Intent Classification).
        * Nếu là hỏi chính sách -> Route sang **RAG Module**.
        * Nếu là hỏi đơn hàng -> Route sang **Order Tool**.
        * [cite_start]Nếu khiếu nại -> Tạo Ticket và gắn nhãn "High Priority" (Use Case: Phân tuyến thông minh [cite: 1]).

#### Module 3.3: Sentiment Analysis
* **Thực hiện:**
    1.  Khi tin nhắn đến, chạy qua model phân tích cảm xúc (Positive/Negative).
    2.  [cite_start]Lưu kết quả vào bảng `Sentiments` [cite: 151, 201] để Admin theo dõi mức độ hài lòng.

---

### PHASE 4: ANALYTICS (NLQ) & FINALIZATION (Tuần 7-8)
[cite_start]**Mục tiêu:** Cho phép Admin hỏi các câu hỏi thống kê phức tạp mà không cần code SQL (Use Case: Dashboard hỏi-đáp NLQ [cite: 1]).

#### Module 4.1: Text-to-SQL Agent
* **Nhiệm vụ:** Biến câu hỏi tự nhiên thành SQL query.
* **Thực hiện:**
    1.  Cung cấp Schema của các bảng `Orders`, `Order_Items` cho LLM.
    2.  Prompt: "Acting as a Data Analyst, generate MySQL query for..."
    3.  User hỏi: "Doanh thu tuần trước là bao nhiêu?" -> AI sinh SQL: `SELECT SUM(total) FROM orders WHERE...`
    4.  Thực thi SQL an toàn (Read-only user) và hiển thị kết quả.

#### Module 4.2: Admin Dashboard & Agent Debugging
* **Thực hiện:**
    1.  Hiển thị biểu đồ từ Module 4.1.
    2.  **Agent Playground (Quan trọng cho đồ án):** Tạo một màn hình cho phép thầy cô xem "Suy nghĩ" của AI (Agent Thoughts/Traces):
        * Input: "Hủy đơn hàng X"
        * Thought: "User muốn hủy đơn -> Kiểm tra trạng thái đơn -> Đơn đang Pending -> Gọi tool hủy -> Trả lời user".
    
#### Module 4.3: Testing & Documentation
* Viết tài liệu hướng dẫn (README).
* Quay video demo kịch bản.

---

## 3. CHECKLIST CÁC TÍNH NĂNG CẦN DEMO (Để đạt điểm cao)

| Chức năng | Loại | Mô tả kịch bản Demo |
| :--- | :--- | :--- |
| **RAG FAQ** | Cơ bản | Upload file PDF chính sách đổi trả. Hỏi bot: "Hàng mua rồi trả được không?" -> Bot trả lời đúng theo file. |
| **Tra cứu đơn** | Agent | Hỏi: "Đơn hàng #ORD-001 đi đến đâu rồi?" -> Bot: "Đơn hàng đang giao, dự kiến mai tới". |
| **Hành động** | Agent | Hỏi: "Tìm giúp tôi giày chạy bộ giá dưới 1 triệu" -> Bot hiển thị list sản phẩm từ DB. |
| **Phân tích** | NLQ | Admin hỏi: "Top 3 sản phẩm bán chạy nhất tháng này?" -> Bot vẽ biểu đồ cột. |
| **Phân loại** | NLP | Khách chat câu chửi thề/bực dọc -> Hệ thống tự đánh dấu Ticket là "Khẩn cấp". |

Bạn có thể sử dụng file này làm đề cương chi tiết để báo cáo tiến độ với giáo viên hướng dẫn.

---

## 4. HƯỚNG DẪN CHẠY DEMO (QUICK START)

### 🎯 Mục Tiêu Demo
Hệ thống demo hoàn chỉnh với **3 tính năng chính**:
1. **Quản lý sản phẩm**: Xem danh sách, tìm kiếm, chi tiết sản phẩm
2. **Chat AI với RAG**: Hỏi đáp dựa trên tài liệu đã upload
3. **Lưu hội thoại**: Conversation memory tự động

### 📋 Yêu Cầu Hệ Thống
- **Python**: 3.9+ (đã cài venv)
- **Node.js**: 16+ (để chạy frontend React)
- **MySQL**: 5.7+ hoặc 8.0
- **Git**: Để clone project

### ⚙️ Bước 1: Cấu Hình Database MySQL

#### Tạo Database
```sql
CREATE DATABASE crm_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'crm_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON crm_demo.* TO 'crm_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Hoặc Dùng Docker (Tùy chọn)
```powershell
cd "d:\Bai Luan\Nam 2025 - 2026\Hoc Ky I\CS434\CS434\CRM-AI-Agent"
docker compose up -d
```

### ⚙️ Bước 2: Setup Backend

#### 2.1. Cấu Hình .env
Mở file `CRM-AI-Agent\.env` và điền thông tin:

```env
# ===== DEMO MODE (Không cần OpenAI API Key) =====
DEMO_MODE=true

# ===== DATABASE =====
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=crm_user
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=crm_demo

DATABASE_URL=mysql+pymysql://crm_user:your_password_here@localhost:3306/crm_demo

# ===== AUTHENTICATION =====
SECRET_KEY=demo-jwt-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ===== CORS (Frontend) =====
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# ===== VECTOR DATABASE =====
CHROMA_PERSIST_DIR=./vector_store

# ===== OPENAI (Tùy chọn - không cần nếu DEMO_MODE=true) =====
OPENAI_API_KEY=sk-optional-for-demo
```

**Lưu ý quan trọng:** 
- Thay `your_password_here` bằng mật khẩu MySQL thật
- `DEMO_MODE=true` sẽ dùng mock LLM, không cần OpenAI API key

#### 2.2. Cài Đặt Dependencies
```powershell
cd "d:\Bai Luan\Nam 2025 - 2026\Hoc Ky I\CS434\CS434\CRM-AI-Agent\backend"
.\venv\Scripts\Activate.ps1
pip install -r ../requirements.txt
```

#### 2.3. Seed Dữ Liệu Demo
```powershell
# Vẫn trong backend directory với venv đã activate
python seed_demo_data.py
```

**Output mong đợi:**
```
🌱 Starting CRM Demo Data Seeding...
📦 Creating database tables...
✅ Tables created successfully!

👤 Seeding demo users...
✅ Created user: admin@crm-demo.com (password: admin123)
✅ Created user: staff@crm-demo.com (password: staff123)
✅ Created user: customer@crm-demo.com (password: customer123)
✅ Created 3 new users

📦 Seeding demo products...
✅ Created product: Laptop Dell XPS 15 (DELL-XPS15-2024)
...
✅ Created 10 new products

✅ Demo data seeding completed successfully!

📋 Login credentials:
   Admin:    admin@crm-demo.com / admin123
   Staff:    staff@crm-demo.com / staff123
   Customer: customer@crm-demo.com / customer123
```

#### 2.4. Khởi Chạy Backend
```powershell
python main.py
```

**Backend sẽ chạy tại:** `http://localhost:8000`

**Kiểm tra health check:**
Mở trình duyệt: http://localhost:8000/health

Kết quả mong đợi: `{"status": "healthy"}`

### ⚙️ Bước 3: Upload Tài Liệu RAG

Backend đã có sẵn 3 file tài liệu demo trong `CRM-AI-Agent\uploads\`:
- `huong_dan_su_dung.md` - Hướng dẫn sử dụng CRM
- `chinh_sach_bao_hanh.md` - Chính sách bảo hành và đổi trả
- `khuyen_mai.md` - Danh sách sản phẩm khuyến mãi

#### Sử dụng Postman/cURL để Upload
```powershell
# Lấy access token trước
$loginBody = @{
    username = "admin@crm-demo.com"
    password = "admin123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -Body "username=admin@crm-demo.com&password=admin123" -ContentType "application/x-www-form-urlencoded"
$token = $response.access_token

# Upload file
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/rag/upload" -Method POST -Headers $headers -Form @{
    file = Get-Item "d:\Bai Luan\Nam 2025 - 2026\Hoc Ky I\CS434\CS434\CRM-AI-Agent\uploads\huong_dan_su_dung.md"
    title = "Hướng dẫn sử dụng"
    category = "Tutorial"
}
```

**Hoặc dùng Postman:**
1. POST `http://localhost:8000/auth/login`
   - Body: `form-data` với `username` và `password`
   - Copy `access_token`

2. POST `http://localhost:8000/rag/upload`
   - Headers: `Authorization: Bearer <token>`
   - Body: `form-data` với key `file` (type: File)
   - Upload cả 3 file `.md`

### ⚙️ Bước 4: Setup Frontend

#### 4.1. Cài Dependencies
```powershell
cd "d:\Bai Luan\Nam 2025 - 2026\Hoc Ky I\CS434\CS434\CRM-AI-Agent\frontend"
npm install
```

#### 4.2. Khởi Chạy Frontend
```powershell
npm run dev
```

**Frontend sẽ chạy tại:** `http://localhost:5173`

### 🎬 Bước 5: Demo Các Chức Năng

#### 5.1. Đăng Nhập
1. Mở http://localhost:5173
2. Sử dụng tài khoản demo:
   - **Admin**: `admin@crm-demo.com` / `admin123`
   - **Staff**: `staff@crm-demo.com` / `staff123`
   - **Customer**: `customer@crm-demo.com` / `customer123`

#### 5.2. Xem Sản Phẩm
- Click menu "📦 Sản phẩm"
- Thấy 10 sản phẩm đã seed
- Dùng thanh tìm kiếm để filter sản phẩm
- **Screenshot này để demo UI**

#### 5.3. Chat với AI
- Click menu "💬 Chat AI"
- Thử các câu hỏi:
  * "Chính sách bảo hành là gì?"
  * "Laptop nào phù hợp cho văn phòng?"
  * "Có khuyến mãi gì trong tháng này?"
  * "Cách đổi trả sản phẩm?"

**Kết quả mong đợi:**
```
🤖 [DEMO MODE - Mock AI Response]

Dựa trên tài liệu, tôi tìm thấy 3 đoạn thông tin liên quan đến câu hỏi: 'Chính sách bảo hành là gì?'.

Thông tin chính:
## Chính Sách Bảo Hành

### Thời Gian Bảo Hành

**Sản phẩm điện tử:**
- Laptop: 24 tháng (bảo hành chính hãng)
- Smartphone: 12 tháng
...

💡 Lưu ý: Đây là phản hồi mô phỏng cho mục đích demo. Trong môi trường production, hệ thống sẽ sử dụng OpenAI GPT để tạo câu trả lời thông minh hơn.
```

- Gửi thêm 2-3 câu hỏi để thấy conversation được lưu
- Conversation ID hiển thị ở dưới cùng
- **Screenshot phần chat để demo RAG + Memory**

### 📸 Checklist Demo Screenshots

Cần chụp màn hình 3 tính năng sau:

1. **Màn hình Login** ✅
   - Hiển thị form đăng nhập với tài khoản demo
   
2. **Màn hình Products** ✅
   - Danh sách 10 sản phẩm với giá, SKU, stock
   - Thanh tìm kiếm hoạt động
   
3. **Màn hình Chat AI** ✅
   - Gửi câu hỏi và nhận phản hồi từ mock LLM
   - Hiển thị conversation ID
   - Lịch sử chat 3-4 tin nhắn

### 🧪 Testing API với cURL/Postman

#### Test 1: Login
```powershell
curl -X POST "http://localhost:8000/auth/login" `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=admin@crm-demo.com&password=admin123"
```

#### Test 2: Get Products
```powershell
# Thay <TOKEN> bằng access_token từ login
curl -X GET "http://localhost:8000/products" `
  -H "Authorization: Bearer <TOKEN>"
```

#### Test 3: Chat RAG
```powershell
curl -X POST "http://localhost:8000/rag/chat" `
  -H "Authorization: Bearer <TOKEN>" `
  -H "Content-Type: application/json" `
  -d '{"message": "Chính sách bảo hành là gì?", "conversation_id": null}'
```

### 🔍 Troubleshooting

**Lỗi: Cannot connect to MySQL**
- Kiểm tra MySQL đã chạy: `mysql -u root -p`
- Kiểm tra `DATABASE_URL` trong `.env`
- Thử: `CREATE DATABASE crm_demo;` nếu chưa tạo

**Lỗi: CORS error ở frontend**
- Kiểm tra `CORS_ORIGINS` trong `.env` có `http://localhost:5173`
- Restart backend sau khi sửa `.env`

**Lỗi: No module named 'langchain'**
- Activate venv: `.\venv\Scripts\Activate.ps1`
- Cài lại: `pip install -r requirements.txt`

**Frontend không hiển thị sản phẩm**
- Kiểm tra backend chạy tại port 8000
- Kiểm tra đã seed data: `python seed_demo_data.py`
- Check console log ở browser (F12)

### 📝 Ghi Chú Quan Trọng

**Demo Mode vs Production:**
- **Demo Mode** (`DEMO_MODE=true`): Dùng mock LLM, không cần OpenAI API key, phản hồi đơn giản
- **Production** (`DEMO_MODE=false`): Cần `OPENAI_API_KEY`, phản hồi thông minh từ GPT-3.5-turbo

**Dữ Liệu:**
- Database được tạo tự động khi chạy `python main.py` lần đầu
- Seed script tạo: 3 users, 10 products
- RAG: 3 file markdown mẫu trong `uploads/`

**Tính Năng Đã Implement:**
✅ Authentication (JWT)
✅ CRUD Products
✅ RAG với ChromaDB
✅ Conversation Memory
✅ Mock LLM cho demo
✅ Frontend React với 3 màn hình

**Tính Năng Chưa Có (Phase tiếp theo):**
⏳ Agent Tools (lookup order, cancel order)
⏳ Sentiment Analysis
⏳ Text-to-SQL (NLQ Analytics)
⏳ Admin Dashboard với charts

### 🎓 Kịch Bản Demo Cho Thầy Cô

**Thời lượng:** 10-15 phút

1. **Giới thiệu** (2 phút)
   - "Em xin demo hệ thống CRM tích hợp AI Agent..."
   - Giải thích 3 tính năng chính

2. **Demo Backend API** (3 phút)
   - Login API → Get token
   - Get products → Hiển thị JSON
   - Upload document → Index thành công

3. **Demo Frontend** (5 phút)
   - Đăng nhập → Màn hình sản phẩm
   - Tìm kiếm sản phẩm
   - Chat với AI → Hỏi về chính sách bảo hành
   - Gửi thêm câu hỏi → Conversation được lưu

4. **Demo Database** (2 phút)
   - Mở MySQL Workbench
   - Show bảng `conversations`, `conversation_messages`
   - Query: `SELECT * FROM conversations ORDER BY created_at DESC LIMIT 5;`

5. **Giải thích Technical** (3 phút)
   - Architecture: FastAPI + React + MySQL + ChromaDB
   - RAG pipeline: Upload → Chunk → Embed → Store → Retrieve → Generate
   - Demo mode: Mock LLM để tránh chi phí OpenAI trong demo

### 📚 Tài Liệu Tham Khảo Thêm

- `PHASE2_SUMMARY.md` - Chi tiết RAG implementation
- `PHASE3_SUMMARY.md` - Chi tiết LLM integration và conversation memory
- `README.md` - Project overview
- API Docs tự động: http://localhost:8000/docs (sau khi chạy backend)