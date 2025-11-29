# ⚡ QUICK START GUIDE

## 🚀 Khởi Động Nhanh (5 Phút)

### Bước 1: Chuẩn Bị Môi Trường

```powershell
# 1. Clone repository (đã có)
cd "d:\Bai Luan\Nam 2025 - 2026\Hoc Ky I\CS434\CS434\CRM-AI-Agent"

# 2. Copy file environment
cp .env.example .env

# 3. Mở .env và thêm OpenAI API Key
# OPENAI_API_KEY=sk-your-key-here
```

### Bước 2: Chạy Với Docker (Khuyến Nghị)

```powershell
# Đảm bảo Docker Desktop đang chạy
docker --version

# Khởi động tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f
```

**Truy cập:**
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Frontend: http://localhost:3000

### Bước 3: Hoặc Chạy Manual (Development)

#### Backend:

```powershell
cd backend

# Tạo virtual environment
python -m venv venv

# Activate (PowerShell)
.\venv\Scripts\Activate.ps1

# Cài đặt dependencies
pip install -r ../requirements.txt

# Chạy server
uvicorn main:app --reload
```

#### Frontend:

```powershell
cd frontend

# Cài đặt dependencies
npm install

# Chạy dev server
npm run dev
```

---

## 📋 Kiểm Tra Hệ Thống

### Test Backend API

```powershell
# Mở browser: http://localhost:8000/docs

# Hoặc dùng curl:
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "CRM-AI-Agent API is running",
  "version": "1.0.0"
}
```

### Test Database Connection

```powershell
# Kết nối MySQL (nếu chạy bằng Docker)
docker exec -it crm_mysql mysql -u crm_user -p

# Password: your_secure_password_here

# Kiểm tra database
SHOW DATABASES;
USE crm_ai_db;
SHOW TABLES;
```

---

## 🎯 Bắt Đầu Làm Việc

### Phase 1: Database Setup (Ngay Bây Giờ)

1. **Tạo Database Schema**

```powershell
cd database/schemas
# Tạo file init.sql với schema MySQL
```

2. **Setup Alembic**

```powershell
cd backend
alembic init alembic
# Chỉnh sửa alembic.ini và alembic/env.py
```

3. **Tạo Models**

```powershell
# Tạo các file trong backend/models/
# - user.py
# - product.py
# - order.py
# - ticket.py
```

4. **Generate Migration**

```powershell
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

---

## 📚 Tài Liệu Tham Khảo

### Docs Đã Tạo
- 📖 [README.md](../README.md) - Tổng quan dự án
- 🚀 [GETTING_STARTED.md](./GETTING_STARTED.md) - Hướng dẫn chi tiết
- 🗓️ [ROADMAP.md](./ROADMAP.md) - Lộ trình 8 tuần

### External Resources
- **FastAPI Tutorial**: https://fastapi.tiangolo.com/tutorial/
- **LangChain Docs**: https://python.langchain.com/docs/get_started/introduction
- **ChromaDB Guide**: https://docs.trychroma.com/getting-started
- **SQLAlchemy Tutorial**: https://docs.sqlalchemy.org/en/20/tutorial/

---

## 🛠️ Các Lệnh Hữu Ích

### Docker Commands

```powershell
# Khởi động services
docker-compose up -d

# Dừng services
docker-compose down

# Xem logs
docker-compose logs -f backend

# Rebuild sau khi thay đổi code
docker-compose up -d --build

# Xóa volumes (reset database)
docker-compose down -v
```

### Python Commands

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Install package mới
pip install <package-name>
pip freeze > ../requirements.txt

# Run tests
pytest
pytest --cov=backend

# Format code
black .
flake8 .
```

### Database Commands

```powershell
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1

# View history
alembic history
```

---

## 🐛 Troubleshooting

### Lỗi: Port 8000 already in use

```powershell
# Tìm process đang dùng port
netstat -ano | findstr :8000

# Kill process (thay PID)
taskkill /PID <PID> /F
```

### Lỗi: MySQL connection refused

```powershell
# Kiểm tra MySQL đang chạy
docker ps | findstr mysql

# Hoặc start lại container
docker start crm_mysql
```

### Lỗi: ModuleNotFoundError

```powershell
# Đảm bảo venv đã activate và cài dependencies
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 📞 Next Steps

1. ✅ **Đọc**: [GETTING_STARTED.md](./GETTING_STARTED.md) để hiểu cấu trúc
2. ✅ **Xem**: [ROADMAP.md](./ROADMAP.md) để biết lộ trình chi tiết
3. 🚀 **Bắt đầu**: Phase 1 - Database & Backend CRUD

**Happy Coding! 🎉**
