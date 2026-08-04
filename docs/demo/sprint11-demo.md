# HÀNH CHÍNH AI
## Sprint 11 Demo

---

# Mục tiêu

Chứng minh hệ thống Hành Chính AI có thể:

- Sinh văn bản bằng AI
- Sinh Word
- Download Word
- Hỗ trợ nhiều AI Provider
- Hoạt động End-to-End

---

# Chuẩn bị

## Backend

Khởi động

uvicorn app.main:app --reload

---

## Ollama

ollama serve

Kiểm tra

ollama list

Model

qwen3:8b

---

## Frontend

npm run dev

---

# Demo 01

Mở

http://localhost:5173

---

# Demo 02

Chọn

Provider

Ollama

---

# Demo 03

Loại văn bản

Công văn

---

# Demo 04

Tiêu đề

Tăng cường chuyển đổi số

---

# Demo 05

Prompt

Soạn công văn về việc tăng cường chuyển đổi số tại UBND xã.

---

# Demo 06

Nhấn

"Tạo bằng AI"

Quan sát

- Loading
- Spinner
- Disable Form

---

# Demo 07

AI sinh nội dung

Hiển thị

Kết quả AI

---

# Demo 08

Backend

Sinh

output/cong_van_xxx.docx

---

# Demo 09

Download

Word

---

# Demo 10

Mở Microsoft Word

Kiểm tra

- Header
- Quốc hiệu
- Tiêu đề
- Nội dung
- Chữ ký

---

# Demo 11

Swagger

/document/generate

PASS

---

# Demo 12

Health

/document/health

PASS

---

# Demo 13

Thử Prompt khác

Ví dụ

Thông báo nghỉ lễ

Quyết định

Kế hoạch

PASS

---

# Demo 14

Đổi Provider

OpenAI

(Nếu có API Key)

PASS

---

# Demo 15

Kết luận

Frontend

PASS

Backend

PASS

Conversation

PASS

Prompt Builder

PASS

Provider Factory

PASS

Ollama

PASS

OpenAI

PASS

Word Generator

PASS

Download

PASS

Health

PASS

Sprint 11

HOÀN THÀNH