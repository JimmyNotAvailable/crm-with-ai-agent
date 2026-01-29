# CRM-AI-Agent Tests

Thư mục này chứa các test cases và scripts kiểm tra cho dự án CRM-AI-Agent.

## Cấu trúc

```
tests/
├── __init__.py              # Module init
├── README.md                # Hướng dẫn này
├── test_api.py              # Test API với TestClient (không cần server)
├── test_api_full.py         # Full test suite với HTTP requests
├── test_complete_api.py     # Complete API test (Health, Auth, RAG)
├── test_login_api.py        # Test đăng nhập
├── check_identity.py        # Kiểm tra database identity schema
├── check_password.py        # Kiểm tra password hash
└── create_test_user.py      # Tạo test user cho testing
```

## Chạy tests

### 1. Test không cần server (TestClient)

```bash
cd <project_root>
python -m pytest tests/test_api.py -v
```

### 2. Test cần server đang chạy

Trước tiên, khởi động server:
```bash
uvicorn backend.main:app --reload
```

Sau đó chạy tests:
```bash
python tests/test_api_full.py
python tests/test_complete_api.py
python tests/test_login_api.py
```

### 3. Scripts kiểm tra database

```bash
python tests/check_identity.py    # Kiểm tra schema
python tests/check_password.py    # Kiểm tra password
python tests/create_test_user.py  # Tạo user test
```

## Với pytest

```bash
# Chạy tất cả tests
pytest tests/ -v

# Chạy với coverage
pytest tests/ --cov=backend --cov-report=html

# Chạy test cụ thể
pytest tests/test_api.py::test_health -v
```

## Lưu ý

- File `test_api.py` sử dụng FastAPI TestClient, không cần khởi động server
- Các file còn lại cần server đang chạy ở `http://127.0.0.1:8000`
- Đảm bảo database đã được khởi tạo trước khi chạy tests
