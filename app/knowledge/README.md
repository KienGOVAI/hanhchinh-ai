# Knowledge Base

Knowledge Base là nơi lưu trữ toàn bộ tri thức phục vụ Hành Chính AI.

Mọi tài liệu trong thư mục này sẽ được Knowledge Engine đọc và sử dụng để hỗ trợ AI sinh văn bản, trả lời câu hỏi và tra cứu thông tin.

---

# Cấu trúc thư mục

```text
knowledge/
│
├── README.md
├── laws/
├── procedures/
├── templates/
├── regulations/
├── faq/
├── examples/
└── local/
```

---

# Quy tắc

- Mỗi tài liệu chỉ nên chứa **một chủ đề**.
- Đặt tên file bằng chữ thường.
- Sử dụng dấu gạch dưới (`_`) thay cho khoảng trắng.
- Mã hóa UTF-8.
- Định dạng Markdown (`.md`).

Ví dụ:

```text
nghi_dinh_30.md

luat_luu_tru.md

ky_so.md
```

---

# Nội dung

Khuyến nghị mỗi file nên có cấu trúc:

```markdown
# Tiêu đề

## Mục đích

...

## Nội dung

...

## Lưu ý

...
```

---

# Không đưa vào Knowledge

Không lưu:

- File Word (.docx)
- File PDF
- Ảnh
- Video
- File tạm
- File sao lưu

Các định dạng này sẽ được hỗ trợ trong các phiên bản tiếp theo.

---

# Nguyên tắc cập nhật

- Một thay đổi nên tương ứng với một commit Git.
- Không sửa trực tiếp nhiều tài liệu trong cùng một commit nếu không liên quan.
- Khi cập nhật văn bản pháp luật, ghi rõ phiên bản và thời điểm cập nhật trong nội dung tài liệu.

---

# Mục đích của từng thư mục

## laws/

Lưu:

- Luật
- Nghị định
- Thông tư
- Quyết định
- Văn bản quy phạm pháp luật

---

## procedures/

Lưu:

- Quy trình nghiệp vụ
- ISO
- Hướng dẫn xử lý hồ sơ
- Quy trình nội bộ

---

## templates/

Lưu:

- Quy chuẩn soạn thảo
- Mẫu nội dung tham khảo
- Hướng dẫn xây dựng văn bản

Không lưu file Word.

---

## regulations/

Lưu:

- Quy chế
- Nội quy
- Quy định nội bộ

---

## faq/

Lưu:

- Câu hỏi thường gặp
- Hướng dẫn sử dụng
- Giải đáp nghiệp vụ

---

## examples/

Lưu:

- Ví dụ văn bản mẫu
- Ví dụ tình huống
- Few-shot Prompt (trong các phiên bản sau)

---

## local/

Lưu:

- Quy trình đặc thù của từng đơn vị triển khai
- Quy định nội bộ riêng
- Tài liệu phục vụ từng địa phương

---

# Roadmap

## Sprint 11

- Markdown Knowledge

## Sprint 12

- Chunking

## Sprint 13

- Embedding

## Sprint 14

- Vector Database

## Sprint 15

- RAG Search

---

# Lưu ý

Knowledge Base là nguồn dữ liệu của Hành Chính AI.

Không chỉnh sửa nội dung nếu chưa được kiểm chứng.

Ưu tiên sử dụng văn bản chính thức của cơ quan nhà nước.