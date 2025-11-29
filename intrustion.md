Chào bạn, đây là nội dung đã được cập nhật để sử dụng hệ quản trị cơ sở dữ liệu **MySQL** cho phần nghiệp vụ, thay vì PostgreSQL.

---

Chào bạn, với tư cách là một Senior AI Engineer và Business Analyst (BA), tôi đã phân tích kỹ lưỡng các tài liệu bạn cung cấp (Use Case UML, ERD, Database Schema, và UI Mockups).

Dưới đây là bản tổng hợp chi tiết về hiện trạng dự án và các đề xuất điều chỉnh phù hợp với quy mô đồ án môn học, tập trung vào thế mạnh là **AI Agent & RAG System**.

### 1. Phân tích chức năng hiện có (AS-IS)
Dựa trên tài liệu thiết kế hệ thống và cơ sở dữ liệu, dự án CRM này đang được thiết kế khá bài bản theo hướng **Omni-channel CRM** tích hợp AI sâu.

#### A. Phân hệ Bán hàng (Sales)
* **Mua sắm hội thoại (Conversational Commerce):** Chatbot hỗ trợ mua hàng.
* **Quản lý đơn hàng:** Quản lý giỏ hàng, thanh toán, theo dõi trạng thái đơn, vận chuyển, đổi trả.
* **Gợi ý sản phẩm (AI Recommendation):** Hệ thống đề xuất Up-sell/Cross-sell.

#### B. Phân hệ Chăm sóc khách hàng (Customer Service)
* **Quản lý Ticket đa kênh:** Tạo ticket từ nhiều nguồn, gán nhân viên xử lý.
* **AI Support (RAG):** Chatbot tự trả lời câu hỏi thường gặp (FAQ) dựa trên Knowledge Base.
* **Phân tuyến thông minh (Smart Routing):** Tự động phân chia công việc cho nhân viên dựa trên quy tắc (Rule-based) hoặc AI.
* **Phân tích cảm xúc (Sentiment Analysis):** Đánh giá cảm xúc khách hàng qua tin nhắn (Tích cực/Tiêu cực).

#### C. Phân hệ Marketing (Automation)
* **Hành trình khách hàng (Customer Journey):** Thiết kế luồng gửi tin nhắn tự động (Email/SMS) theo điều kiện.
* **Nhắc giỏ hàng:** Tự động nhắc nhở khi khách bỏ quên giỏ hàng.

#### D. Phân hệ Quản trị & AI (Admin & Analytics)
* **Dashboard hỏi đáp (NLQ):** Hỏi đáp số liệu bằng ngôn ngữ tự nhiên (Natural Language Querying).
* **Quản lý mô hình AI:** Quản lý các version của ML Models và kết quả dự đoán.
* **Quản lý tri thức (Knowledge Base):** Soạn thảo, gắn thẻ bài viết để phục vụ RAG.

---

### 2. Đánh giá & Đề xuất chức năng cần thêm/bớt (TO-BE)
Vì đây là **đồ án môn học**, chúng ta cần "tinh gọn" các phần nghiệp vụ phức tạp (như Logistics, Payment Gateway thật) để tập trung "khoe" công nghệ AI/Python/RAG.

#### Các chức năng NÊN GIỮ & LÀM SÂU (Core Features):
1.  **AI RAG Chatbot (MVP phải có):**
    * *Hiện tại:* Đã có bảng `KB_Articles`.
    * *Nâng cấp:* Xây dựng Pipeline "Ingestion" cho phép Admin upload file PDF/Docx chính sách bán hàng. Hệ thống tự động chunking và lưu vào Vector DB (ChromaDB/Milvus). Chatbot trả lời có trích dẫn nguồn.
2.  **Phân loại Ticket tự động (AI Classification):**
    * *Hiện tại:* Có `Smart Routing`.
    * *Cụ thể hóa:* Khi khách chat "Hàng bị vỡ", AI Agent tự động tag là "Complaint" và gán độ ưu tiên "High".
3.  **Chat với dữ liệu (NLQ/Text-to-SQL):**
    * *Hiện tại:* Có `Dashboard hỏi-đáp`.
    * *Cụ thể hóa:* Admin hỏi "Doanh thu tuần này bao nhiêu?", AI Agent sinh câu lệnh SQL query (MySQL dialect) vào bảng `Orders` và trả về con số/biểu đồ.

#### Các chức năng CẦN THÊM (Để đúng chất AI Agent System):
1.  **AI Agent "Tool Use" (Function Calling):**
    * Cho phép Chatbot không chỉ trả lời (RAG) mà còn **thực hiện hành động**.
    * *Ví dụ:* Khách hàng chat "Hủy đơn hàng #123 giúp tôi". AI Agent kiểm tra trạng thái đơn -> Nếu chưa ship thì gọi hàm `cancel_order(id)` -> Thông báo thành công.
2.  **Agent Dashboard (AI Playground):**
    * Thêm một giao diện trong Admin để "Debug" AI. Cho phép xem: Prompt đã gửi đi là gì? Context lấy từ RAG là đoạn nào? Tại sao AI lại trả lời như vậy? (Quan trọng cho đồ án để thầy cô thấy được logic bên dưới).
3.  **Giả lập đa kênh (Omni-channel Simulation):**
    * Thay vì chỉ chat trên Web, hãy tích hợp **Telegram Bot** hoặc **Facebook Messenger** (dùng API thật). Điều này chứng minh tính thực tế cao hơn.

#### Các chức năng NÊN GIẢM TẢI (Tránh lan man):
* *Vận chuyển/Shipments:* Chỉ cần lưu trạng thái đơn giản, không cần tích hợp API Giao Hàng Nhanh/Viettel Post thật.
* *Marketing Automation phức tạp:* Bỏ qua phần kéo thả Journey phức tạp (`Journey_Nodes`, `Journey_Edges`). Thay vào đó chỉ làm chức năng "Gửi email hàng loạt cho tập khách hàng được AI gợi ý".

---

### 3. Sơ đồ kiến trúc đề xuất (High-level Architecture)

Để bạn hình dung hệ thống AI Agent, tôi đề xuất mô hình sau:

* **Frontend:** ReactJS/VueJS (Dựa trên HTML/CSS bạn đã có).
* **Backend:** Python (FastAPI/Flask) - *Bắt buộc vì làm AI*.
* **AI Framework:** LangChain hoặc LlamaIndex.
* **Database:** **MySQL** (lưu nghiệp vụ) + ChromaDB/FAISS (lưu Vector cho RAG).

### 4. Lộ trình triển khai (Roadmap cho đồ án)

1.  **Tuần 1-2:** Chốt DB Schema (dựa trên file `database_CRM.drawio` nhưng bỏ bớt các bảng Marketing phức tạp). Dựng Backend CRUD cơ bản (User, Product, Order) kết nối với MySQL.
2.  **Tuần 3-4:** Tích hợp **RAG Pipeline**. Viết API upload tài liệu -> Embed -> Lưu Vector. Viết API Chat dùng LLM (OpenAI/Gemini API) truy vấn Vector.
3.  **Tuần 5-6:** Xây dựng **AI Agent** có khả năng query đơn hàng (Text-to-SQL, sử dụng cú pháp MySQL) và thực hiện hành động (Function Calling).
4.  **Tuần 7-8:** Ghép UI, hoàn thiện Dashboard thống kê và kịch bản demo.

---