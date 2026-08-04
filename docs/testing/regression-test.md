# Regression Test - Sprint 11.9

## Mục tiêu

Đảm bảo toàn bộ quy trình sinh văn bản AI hoạt động ổn định sau khi tích hợp Frontend và Backend.

---

# Test Case 01

Tên:

Sinh công văn bằng Ollama

Điều kiện:

- Ollama đang chạy
- Backend đang chạy
- Frontend đang chạy

Thực hiện:

1. Chọn Provider = Ollama
2. Chọn loại văn bản = Công văn
3. Nhập tiêu đề
4. Nhập Prompt
5. Nhấn "Tạo bằng AI"

Kết quả mong đợi:

- Không lỗi
- Hiện Loading
- AI sinh nội dung
- Sinh file Word
- Trả về file_name

PASS / FAIL

---

# Test Case 02

Tên:

Prompt rỗng

Thực hiện:

Để Prompt trống

Kết quả mong đợi:

Không gọi API

PASS / FAIL

---

# Test Case 03

Tên:

Tiêu đề rỗng

Kết quả mong đợi:

Disable nút

PASS / FAIL

---

# Test Case 04

Tên:

Provider không tồn tại

Request

{
    "provider":"abc"
}

Kết quả mong đợi

400 Bad Request

PASS / FAIL

---

# Test Case 05

Tên:

Backend tắt

Thực hiện

Tắt FastAPI

Kết quả

Hiện thông báo lỗi

PASS / FAIL

---

# Test Case 06

Tên:

Ollama tắt

Thực hiện

Tắt Ollama

Kết quả

Hiện lỗi kết nối

PASS / FAIL

---

# Test Case 07

Tên:

Sinh Word

Kết quả

output/

Có file

PASS / FAIL

---

# Test Case 08

Tên:

Download Word

Kết quả

/document/download/{filename}

Tải thành công

PASS / FAIL

---

# Test Case 09

Tên:

Copy nội dung

Kết quả

Clipboard có nội dung

PASS / FAIL

---

# Test Case 10

Tên:

Loading

Kết quả

Spinner hiển thị

Form Disable

PASS / FAIL

---

# Test Case 11

Tên:

Nội dung AI

Kết quả

Không rỗng

PASS / FAIL

---

# Test Case 12

Tên:

Word mở được

Kết quả

Microsoft Word mở bình thường

PASS / FAIL

---

# Test Case 13

Tên:

Swagger

POST

/document/generate

PASS / FAIL

---

# Test Case 14

Tên:

Health

GET

/document/health

PASS / FAIL

---

# Test Case 15

Tên:

Sinh liên tục 10 lần

Kết quả

Không crash

PASS / FAIL

---

# Kết quả Sprint

| Module | Kết quả |
|---------|----------|
| Frontend | PASS |
| Backend | PASS |
| Ollama | PASS |
| Word Generator | PASS |
| Download | PASS |
| Conversation | PASS |
| API | PASS |

Sprint 11.9

Regression Test

PASS