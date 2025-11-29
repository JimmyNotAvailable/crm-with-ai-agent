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