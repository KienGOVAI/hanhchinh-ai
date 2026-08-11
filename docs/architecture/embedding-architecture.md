# Embedding Architecture

## Hành Chính AI — Sprint 12

---

## 1. Mục tiêu

Embedding Layer chịu trách nhiệm chuyển nội dung KnowledgeChunk thành vector số.

Vector được sử dụng cho:

- Semantic Search.
- Similarity Search.
- Retrieval.
- RAG.

Embedding Layer không chịu trách nhiệm:

- Lưu Vector.
- Search Vector.
- Gọi AI sinh nội dung.
- Tạo văn bản Word.

---

## 2. Vị trí trong kiến trúc

```text
Document
   ↓
Parser
   ↓
Chunker
   ↓
KnowledgeChunk
   ↓
EmbeddingService
   ↓
EmbeddingProvider
   ↓
Vector
   ↓
VectorStore