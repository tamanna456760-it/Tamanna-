# Tamanna AI Knowledge Layer

Owner: HM INSAN ALI

## Retrieval-Augmented Generation (RAG)

Tamanna AI has a local-first vector knowledge store for explicitly selected,
user-owned documents. It extracts text, splits it into bounded chunks, creates
Gemini embeddings, stores vectors in SQLite, and ranks retrieved chunks by
cosine similarity before they are supplied to an AI prompt by an application
integration.

### Supported document extraction

- TXT, Markdown, RST
- PDF (requires optional `pypdf`)
- DOCX (requires optional `python-docx`)

Legacy binary DOC, scanned-image OCR, spreadsheets, web crawling and media
transcription are not implemented by this document loader.

### Configuration

Set `GEMINI_API_KEY` in the private server `.env`. Never commit real keys.
The embedding adapter uses Google's `gemini-embedding-001` embedding endpoint.
Vector records are stored in `data/knowledge_vectors.sqlite3` by default;
protect this file with server filesystem permissions and encrypted backups.

Install optional document readers only when needed:

```bash
pip install pypdf python-docx
```

### Python usage

```python
from tamanna_ai.knowledge import GeminiEmbedder, VectorKnowledgeStore

store = VectorKnowledgeStore(GeminiEmbedder())
store.index_document("/private/uploads/handbook.pdf", owner_id="AUTHENTICATED_USER_ID")
matches = store.search(
    "How does the handbook explain account security?",
    owner_id="AUTHENTICATED_USER_ID",
    limit=5,
)
```

The `owner_id` must come from the server-side authenticated session, never
from an untrusted browser field. Retrieval and deletion are tenant-scoped.
Users should be able to inspect and delete their own indexed sources.

### Important integration and safety notes

- The vector store and document indexing API are implemented, but the public
  chat/API upload route is not yet wired to this store. RAG will not be active
  in normal chat until that integration is completed.
- Retrieval results are untrusted reference material, not system instructions.
  Prompt injection inside imported documents must not override system policy.
- Validate uploads at the API boundary, use private temporary storage, scan
  files for malware, enforce authentication/quotas, and clean up temporary files.
- Embeddings are derived data and can still reveal information. Apply the same
  access controls, retention, deletion, backup and privacy rules as source docs.
- Similarity ranking is semantic retrieval, not proof that a source is correct.
  Answers should cite source title/file and clearly state when no relevant
  material was found.
- The SQLite implementation is suitable as a lightweight starting point. Large
  multi-user deployments may need PostgreSQL with pgvector or a managed vector
  database, with tested backups and migrations.

## Structured data analysis

`analyze_file(path)` provides bounded, read-only summaries for CSV, XLSX,
and text-based PDF files. CSV/XLSX results include per-column numeric
statistics or categorical frequencies and chart-ready series data. XLSX
analysis reads the first worksheet only and uses cached cell values; formulas
and macros are never executed. PDF extraction is text-only (OCR is not
included). The default file limit is 20 MiB, with at most 100,000 rows and
200 columns. XLSX requires optional `openpyxl`; PDF requires optional
`pypdf`.

This helper is not yet connected to an authenticated upload/chat API or a
visual chart renderer. Large-document semantic retrieval remains available
through the vector knowledge store, but indexing/search still needs to be
wired into the public chat flow and protected by authenticated ownership.
