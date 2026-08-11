# Parser Architecture

## Hành Chính AI — Sprint 12

---

## 1. Mục tiêu

Task 12.3 định nghĩa kiến trúc Parser cho Knowledge Base.

Parser có nhiệm vụ:

- Đọc tài liệu gốc.
- Trích xuất nội dung.
- Chuẩn hóa nội dung.
- Giữ metadata về vị trí nội dung.
- Chuẩn bị dữ liệu cho Chunking Engine.

Các định dạng Parser ban đầu:

- PDF
- DOCX
- TXT

Task này chỉ thiết kế kiến trúc.

Chưa triển khai Parser thực tế.

---

# 2. Nguyên tắc thiết kế

## 2.1. Parser độc lập với Knowledge Service

Knowledge Service không được biết chi tiết cách đọc PDF, DOCX hoặc TXT.

Thay vào đó:

```text
KnowledgeService
       │
       ▼
ParserFactory
       │
       ▼
BaseParser
       │
 ┌─────┼─────┐
 ▼     ▼     ▼
PDF   DOCX   TXT