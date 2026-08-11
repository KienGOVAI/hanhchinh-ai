# Knowledge Models & Database Schema

## Hành Chính AI — Sprint 12

---

## 1. Mục tiêu

Task 12.2 định nghĩa mô hình dữ liệu cho Knowledge Base.

Knowledge Base cần quản lý:

- Tài liệu gốc.
- Nguồn tài liệu.
- Metadata.
- Các Chunk được trích xuất từ tài liệu.
- Vị trí Chunk trong tài liệu.
- Trạng thái xử lý.
- Thông tin phục vụ Retrieval và Citation.

Task này chỉ thiết kế mô hình dữ liệu.

Chưa triển khai:

- Parser.
- Embedding.
- Vector Store.
- Retriever.
- RAG.

---

# 2. Nguyên tắc

## 2.1. Document là thực thể gốc

Một tài liệu có thể có nhiều Chunk.

Quan hệ:

Document 1 ──────── N Chunk

---

## 2.2. Chunk phải truy ngược được về Document

Mỗi Chunk bắt buộc có:

- document_id
- nội dung
- thứ tự
- vị trí trong tài liệu

Điều này phục vụ Citation.

---

## 2.3. Metadata không được trộn vào nội dung

Thông tin như:

- Cơ quan ban hành.
- Ngày ban hành.
- Loại văn bản.
- Số hiệu.
- Trạng thái.

được quản lý dưới dạng metadata.

---

# 3. Entity: KnowledgeDocument

Đại diện cho tài liệu được đưa vào Knowledge Base.

Các trường:

| Field | Type | Required | Description |
|---|---|---:|---|
| id | UUID | Yes | ID tài liệu |
| title | String | Yes | Tên tài liệu |
| filename | String | Yes | Tên file gốc |
| document_type | String | Yes | Loại tài liệu |
| source_type | String | Yes | Loại nguồn |
| organization | String | No | Cơ quan ban hành |
| document_number | String | No | Số hiệu |
| issued_date | Date | No | Ngày ban hành |
| effective_date | Date | No | Ngày hiệu lực |
| status | String | Yes | Trạng thái |
| storage_path | String | Yes | Đường dẫn file gốc |
| mime_type | String | No | MIME type |
| file_size | Integer | No | Kích thước file |
| checksum | String | No | Hash file |
| created_at | DateTime | Yes | Ngày tạo |
| updated_at | DateTime | Yes | Ngày cập nhật |

---

# 4. Document Type

Các loại tài liệu ban đầu:

```text
nghi_quyet
chi_thi
quyet_dinh
cong_van
ke_hoach
thong_bao
quy_che
bao_cao
van_ban_phap_luat
khac