# 📌 Trustie – Backend Service

## 📝 Giới thiệu  
**Trustie** là hệ thống **phát hiện và cảnh báo lừa đảo qua điện thoại** dành cho người cao tuổi, được xây dựng với:  
- ⚡ **FastAPI** – Framework Python nhẹ, hiệu năng cao để xây dựng API  
- 🛢 **PostgreSQL** – Hệ quản trị cơ sở dữ liệu quan hệ mạnh mẽ, lưu trữ thông tin số điện thoại, báo cáo và cảnh báo  
- 🤖 **Python AI Libraries** – Tích hợp các mô hình trí tuệ nhân tạo (ML/NLP) để phân tích nội dung cuộc gọi (speech-to-text), phát hiện dấu hiệu lừa đảo và đánh giá rủi ro  

Hệ thống cho phép:
- Kiểm tra số điện thoại có khả năng lừa đảo  
- Báo cáo số điện thoại đáng ngờ  
- Tự động gửi cảnh báo tới người thân được liên kết  
- Phân tích nội dung cuộc gọi và hình ảnh liên quan để nhận diện nguy cơ  

---

## 🏗 Kiến trúc hệ thống (Backend)  
- **FastAPI** – Xử lý request/response, cung cấp API RESTful  
- **PostgreSQL** – Lưu trữ dữ liệu người dùng, số điện thoại, báo cáo, cảnh báo, lịch sử kiểm tra  
- **SQLAlchemy** – ORM mapping giữa Python objects <-> bảng dữ liệu  
- **AI Analysis Module** – Sử dụng thư viện AI (transformers, speech-to-text, OCR…) để phân tích dữ liệu  

---

## 🚀 Hướng dẫn chạy dự án

### 1. **Cài đặt yêu cầu môi trường**  
- Python **3.9+**  
- PostgreSQL đã cài đặt sẵn (hoặc chạy bằng Docker)  

### 2. **Clone dự án**  
```bash
git clone https://github.com/your-repo/trustie-backend.git
cd trustie-backend
```

### 3. **Tạo virtual environment và cài thư viện**  
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### 4. **Cấu hình kết nối cơ sở dữ liệu**  
Chỉnh sửa file `.env` (hoặc file config)  
```env
DATABASE_URL=postgresql://username:password@localhost:5432/trustie_db
```

### 5. **Khởi tạo cơ sở dữ liệu**  
```bash
alembic upgrade head
```

### 6. **Chạy server với Uvicorn**  
```bash
uvicorn back-end.main:app --reload
```

API sẽ chạy tại:  
```
http://localhost:8000
```

### 7. **Truy cập tài liệu API**  
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)  
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)  

