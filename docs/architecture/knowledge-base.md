# Knowledge Base Architecture

## Hành Chính AI — Sprint 12

---

## 1. Mục đích

Knowledge Base là nền tảng tri thức của Hành Chính AI, cho phép hệ thống tiếp nhận, lưu trữ, phân tích, tìm kiếm và cung cấp tài liệu làm Context cho AI.

Mục tiêu:

- Quản lý tài liệu hành chính.
- Quản lý văn bản pháp luật.
- Trích xuất nội dung tài liệu.
- Chia tài liệu thành các đoạn có ý nghĩa.
- Tìm kiếm theo ngữ nghĩa.
- Cung cấp Context cho AI.
- Hỗ trợ trích dẫn nguồn.
- Làm nền tảng cho RAG.

---

## 2. Nguyên tắc kiến trúc

### 2.1. Không phá vỡ kiến trúc Sprint 11

Knowledge Base được tích hợp bổ sung vào hệ thống hiện tại.

Không thay thế:

- AIService
- ProviderFactory
- PromptBuilder
- ContextBuilder
- DocumentService
- DocumentBuilder
- Template Engine

---

### 2.2. Tách biệt các tầng

Knowledge Base được chia thành các tầng:

1. Document
2. Parser
3. Chunking
4. Embedding
5. Vector Store
6. Retrieval
7. RAG
8. Citation

Mỗi tầng có trách nhiệm riêng.

---

## 3. Kiến trúc tổng thể

```text
                    USER
                      │
                      ▼
               React Frontend
                      │
                      ▼
                 FastAPI API
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
   Document Service       Knowledge Service
                                  │
                  ┌───────────────┼───────────────┐
                  │               │               │
                  ▼               ▼               ▼
               Parser          Chunker         Metadata
                  │               │
                  └───────┬───────┘
                          ▼
                     Embedding
                          │
                          ▼
                    Vector Store
                          │
                          ▼
                      Retriever
                          │
                          ▼
                 Knowledge Context
                          │
                          ▼
                   ContextBuilder
                          │
                          ▼
                   PromptBuilder
                          │
                          ▼
                      AIService
                          │
                    ┌─────┴─────┐
                    ▼           ▼
                  Ollama      OpenAI
                    │           │
                    └─────┬─────┘
                          ▼
                     AI Response
                          │
                          ▼
                       Citation