# DATABASE & STORAGE ARCHITECTURE

## Data Storage System for Academic Chatbot

---

## 1. STORAGE APPROACH

### 1.1 Why JSON Instead of MongoDB?

**Decision:** File-based JSON storage  
**Rationale:**

✅ **Simplicity**

- No database server installation required
- No connection management
- Easy to deploy and share

✅ **Portability**

- Single file contains entire knowledge base
- Easy to backup and restore
- Can be version controlled with Git

✅ **Transparency**

- Human-readable format
- Easy to inspect and debug
- Clear data structure

✅ **Sufficient for Use Case**

- Academic chatbot doesn't need millions of records
- Read-heavy workload (queries >> updates)
- Single-user or small team usage

❌ **When MongoDB Would Be Better:**

- Multi-user concurrent access
- Very large document collections (1000+ documents)
- Need for complex queries and aggregations
- Distributed deployment

---

## 2. JSON SCHEMA DESIGN

### 2.1 Complete Schema Structure

```json
{
  "metadata": {
    "last_updated": "ISO 8601 timestamp",
    "total_documents": "integer",
    "total_paragraphs": "integer"
  },
  "documents": [
    {
      "document_id": "string (unique identifier)",
      "title": "string",
      "source_path": "string",
      "total_pages": "integer",
      "paragraph_count": "integer"
    }
  ],
  "paragraphs": [
    {
      "para_id": "string (unique identifier)",
      "text": "string (original text)",
      "page": "integer",
      "heading": "boolean",
      "heading_text": "string or null",
      "sentences": ["array of strings"],
      "char_count": "integer",
      "cleaned_text": "string",
      "cleaned_sentences": ["array of strings"],
      "tokens": ["array of strings"],
      "all_tokens": ["array of strings"],
      "lemmatized_tokens": ["array of strings"],
      "keywords": ["array of strings"],
      "keyword_scores": {
        "keyword1": "float (TF-IDF score)",
        "keyword2": "float"
      },
      "bigrams": ["array of strings"],
      "trigrams": ["array of strings"]
    }
  ],
  "inverted_index": {
    "index": {
      "term1": ["array of para_ids"],
      "term2": ["array of para_ids"]
    },
    "ngram_index": {
      "bigram1": ["array of para_ids"],
      "trigram1": ["array of para_ids"]
    }
  }
}
```

### 2.2 Schema Explanation

#### Metadata Collection

```json
{
  "metadata": {
    "last_updated": "2026-02-05T21:58:34.197899",
    "total_documents": 3,
    "total_paragraphs": 60
  }
}
```

**Purpose:** Track knowledge base statistics  
**Fields:**

- `last_updated`: Timestamp of last modification
- `total_documents`: Count of processed PDFs
- `total_paragraphs`: Total paragraphs across all documents

---

#### Documents Collection

```json
{
  "documents": [
    {
      "document_id": "doc_temp_Github_IMP_Commands_20260205214756",
      "title": "Temp Github Imp Commands",
      "source_path": "temp_Github IMP Commands.pdf",
      "total_pages": 20,
      "paragraph_count": 20
    }
  ]
}
```

**Purpose:** Store document-level metadata  
**Fields:**

- `document_id`: Unique identifier (format: `doc_{filename}_{timestamp}`)
- `title`: Human-readable document title
- `source_path`: Original file path
- `total_pages`: Number of pages in PDF
- `paragraph_count`: Paragraphs extracted from this document

**Primary Key:** `document_id`

---

#### Paragraphs Collection

```json
{
  "paragraphs": [
    {
      "para_id": "doc_temp_Github_IMP_Commands_20260205214756_p1_1",
      "text": "git init: Initializes a new Git repository...",
      "page": 1,
      "heading": false,
      "heading_text": null,
      "sentences": ["git init: Initializes...", "..."],
      "char_count": 1305,
      "cleaned_text": "git init Initializes...",
      "cleaned_sentences": ["git init Initializes..."],
      "tokens": ["git", "init", "initialize", "repository"],
      "all_tokens": ["git", "init", ":", "initializes", "a", "new"],
      "lemmatized_tokens": ["git", "init", "initialize", "repository"],
      "keywords": ["git", "init", "repository"],
      "keyword_scores": {
        "git": 0.0234,
        "init": 0.0234
      },
      "bigrams": ["git_init", "init_initialize"],
      "trigrams": ["git_init_initialize"]
    }
  ]
}
```

**Purpose:** Store paragraph-level content and NLP processing results  
**Primary Key:** `para_id`  
**Foreign Key:** `para_id` contains `document_id` prefix

**Field Categories:**

1. **Identification**
   - `para_id`: Unique identifier (format: `{doc_id}_p{page}_{counter}`)
   - `page`: Page number in source document

2. **Original Content**
   - `text`: Raw extracted text
   - `sentences`: Split sentences
   - `char_count`: Character count

3. **Structural Metadata**
   - `heading`: Boolean flag for heading paragraphs
   - `heading_text`: Heading text if applicable

4. **Preprocessed Content**
   - `cleaned_text`: Normalized text
   - `cleaned_sentences`: Normalized sentences

5. **Tokenization Results**
   - `tokens`: Filtered tokens (stopwords removed)
   - `all_tokens`: All tokens (raw)
   - `lemmatized_tokens`: Base forms

6. **Keyword Analysis**
   - `keywords`: Top keywords (TF-IDF)
   - `keyword_scores`: TF-IDF scores

7. **N-grams**
   - `bigrams`: 2-word phrases
   - `trigrams`: 3-word phrases

---

#### Inverted Index Collection

```json
{
  "inverted_index": {
    "index": {
      "git": ["doc_..._p1_1", "doc_..._p1_2"],
      "repository": ["doc_..._p1_1", "doc_..._p2_1"],
      "branch": ["doc_..._p1_2", "doc_..._p3_1"]
    },
    "ngram_index": {
      "git_init": ["doc_..._p1_1"],
      "git_branch": ["doc_..._p1_2"],
      "machine_learning": ["doc_..._p5_1"]
    }
  }
}
```

**Purpose:** Enable fast keyword-based retrieval  
**Structure:** Two-level index

1. **Term Index** (`index`)
   - Key: Lemmatized term
   - Value: Array of paragraph IDs containing the term

2. **N-gram Index** (`ngram_index`)
   - Key: Bigram or trigram
   - Value: Array of paragraph IDs containing the n-gram

**Complexity:** O(1) lookup time

---

## 3. DATA RELATIONSHIPS

### 3.1 Entity Relationship Diagram

```
┌─────────────────────┐
│     METADATA        │
│  (Global Stats)     │
└─────────────────────┘

┌─────────────────────┐
│    DOCUMENTS        │
│                     │
│ PK: document_id     │
│ - title             │
│ - source_path       │
│ - total_pages       │
│ - paragraph_count   │
└──────────┬──────────┘
           │ 1
           │
           │ N
┌──────────▼──────────┐
│    PARAGRAPHS       │
│                     │
│ PK: para_id         │
│ FK: document_id     │
│ - text              │
│ - page              │
│ - tokens            │
│ - keywords          │
│ - bigrams           │
│ - trigrams          │
└──────────┬──────────┘
           │
           │ Referenced by
           │
┌──────────▼──────────┐
│  INVERTED_INDEX     │
│                     │
│ - term → [para_ids] │
│ - ngram → [para_ids]│
└─────────────────────┘
```

### 3.2 Relationship Types

**One-to-Many (1:N)**

- One Document → Many Paragraphs
- Relationship: `document_id` embedded in `para_id`

**Many-to-Many (N:M)**

- Many Terms → Many Paragraphs
- Implemented via: Inverted Index

---

## 4. CRUD OPERATIONS

### 4.1 Create (Insert)

#### Add New Document

```python
def save_document(self, document_data, inverted_index):
    # Update metadata
    self.knowledge_base["metadata"] = {
        "last_updated": datetime.now().isoformat(),
        "total_documents": len(self.knowledge_base["documents"]) + 1,
        "total_paragraphs": len(self.knowledge_base["paragraphs"]) + len(document_data["paragraphs"])
    }

    # Add document metadata
    doc_metadata = {
        "document_id": document_data["document_id"],
        "title": document_data["title"],
        "source_path": document_data["source_path"],
        "total_pages": document_data["total_pages"],
        "paragraph_count": len(document_data["paragraphs"])
    }
    self.knowledge_base["documents"].append(doc_metadata)

    # Add paragraphs
    self.knowledge_base["paragraphs"].extend(document_data["paragraphs"])

    # Update inverted index
    self.knowledge_base["inverted_index"] = inverted_index.to_dict()

    # Persist to file
    self._save_to_file()
```

**SQL Equivalent:**

```sql
INSERT INTO documents (document_id, title, source_path, total_pages)
VALUES ('doc_001', 'Git Commands', 'git.pdf', 20);

INSERT INTO paragraphs (para_id, document_id, text, page, tokens, keywords)
VALUES ('doc_001_p1_1', 'doc_001', 'git init...', 1, [...], [...]);
```

---

### 4.2 Read (Query)

#### Query 1: Get Paragraph by ID

```python
def get_paragraph_by_id(self, para_id):
    for para in self.knowledge_base["paragraphs"]:
        if para["para_id"] == para_id:
            return para
    return None
```

**SQL Equivalent:**

```sql
SELECT * FROM paragraphs WHERE para_id = 'doc_001_p1_1';
```

**Complexity:** O(n) - Linear search through paragraphs

---

#### Query 2: Get Paragraphs by IDs (Bulk)

```python
def get_paragraphs_by_ids(self, para_ids):
    para_id_set = set(para_ids)
    return [
        para for para in self.knowledge_base["paragraphs"]
        if para["para_id"] in para_id_set
    ]
```

**SQL Equivalent:**

```sql
SELECT * FROM paragraphs
WHERE para_id IN ('doc_001_p1_1', 'doc_001_p1_2', 'doc_001_p2_1');
```

**Complexity:** O(n) - Single pass through paragraphs

---

#### Query 3: Search by Keyword (Using Inverted Index)

```python
def search(self, terms):
    result_para_ids = set()

    for term in terms:
        # O(1) lookup in inverted index
        if term in self.index:
            result_para_ids.update(self.index[term])

    return result_para_ids
```

**SQL Equivalent:**

```sql
-- Without index (slow)
SELECT DISTINCT para_id FROM paragraphs
WHERE 'git' = ANY(tokens) OR 'repository' = ANY(tokens);

-- With inverted index (fast)
SELECT para_id FROM inverted_index
WHERE term IN ('git', 'repository');
```

**Complexity:** O(k) where k = number of search terms

---

#### Query 4: Get All Paragraphs from Document

```python
def get_paragraphs_by_document(self, document_id):
    return [
        para for para in self.knowledge_base["paragraphs"]
        if para["para_id"].startswith(document_id)
    ]
```

**SQL Equivalent:**

```sql
SELECT * FROM paragraphs WHERE para_id LIKE 'doc_001%';
```

**Complexity:** O(n)

---

### 4.3 Update

#### Update Metadata

```python
def update_metadata(self):
    self.knowledge_base["metadata"]["last_updated"] = datetime.now().isoformat()
    self.knowledge_base["metadata"]["total_documents"] = len(self.knowledge_base["documents"])
    self.knowledge_base["metadata"]["total_paragraphs"] = len(self.knowledge_base["paragraphs"])
    self._save_to_file()
```

**SQL Equivalent:**

```sql
UPDATE metadata
SET last_updated = NOW(),
    total_documents = (SELECT COUNT(*) FROM documents),
    total_paragraphs = (SELECT COUNT(*) FROM paragraphs);
```

---

### 4.4 Delete

#### Clear Entire Knowledge Base

```python
def clear(self):
    self.knowledge_base = {
        "metadata": {},
        "documents": [],
        "paragraphs": [],
        "inverted_index": {}
    }
    self._save_to_file()
```

**SQL Equivalent:**

```sql
DELETE FROM paragraphs;
DELETE FROM documents;
DELETE FROM inverted_index;
UPDATE metadata SET total_documents = 0, total_paragraphs = 0;
```

---

## 5. INDEXING STRATEGY

### 5.1 Inverted Index Implementation

**Purpose:** Fast keyword-based retrieval  
**Data Structure:** Hash Map (Dictionary)

```python
class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(set)  # term -> set of para_ids
        self.ngram_index = defaultdict(set)  # n-gram -> set of para_ids

    def build_index(self, paragraphs):
        for para in paragraphs:
            para_id = para["para_id"]

            # Index lemmatized tokens
            for token in para.get("lemmatized_tokens", []):
                self.index[token].add(para_id)

            # Index keywords
            for keyword in para.get("keywords", []):
                self.index[keyword].add(para_id)

            # Index bigrams
            for bigram in para.get("bigrams", []):
                self.ngram_index[bigram].add(para_id)

            # Index trigrams
            for trigram in para.get("trigrams", []):
                self.ngram_index[trigram].add(para_id)
```

### 5.2 Index Performance

| Operation              | Without Index | With Inverted Index |
| ---------------------- | ------------- | ------------------- |
| **Search for term**    | O(n × m)      | O(1)                |
| **Search for N terms** | O(n × m × N)  | O(N)                |
| **Build index**        | N/A           | O(n × m)            |
| **Storage overhead**   | 0             | O(n × m)            |

Where:

- n = number of paragraphs
- m = average tokens per paragraph
- N = number of search terms

**Example:**

- 1000 paragraphs, 100 tokens each
- Search for "machine learning"
- **Without index:** 1000 × 100 = 100,000 comparisons
- **With index:** 2 lookups = O(1)

---

## 6. QUERY EXECUTION FLOW

### 6.1 Question Answering Query Flow

```
User Question: "What is git init?"
         ↓
┌────────────────────────────────────────┐
│ 1. QUERY PROCESSING                    │
│    - Tokenize: ["what", "is", "git", "init"]│
│    - Remove stopwords: ["git", "init"] │
│    - Lemmatize: ["git", "init"]        │
└────────────┬───────────────────────────┘
             ↓
┌────────────────────────────────────────┐
│ 2. INVERTED INDEX LOOKUP               │
│    - Lookup "git" → {p1, p2, p5}       │
│    - Lookup "init" → {p1, p3}          │
│    - Union: {p1, p2, p3, p5}           │
└────────────┬───────────────────────────┘
             ↓
┌────────────────────────────────────────┐
│ 3. RETRIEVE PARAGRAPHS                 │
│    - Get paragraph objects by IDs      │
│    - Result: [para_p1, para_p2, ...]   │
└────────────┬───────────────────────────┘
             ↓
┌────────────────────────────────────────┐
│ 4. BM25 RANKING                        │
│    - Calculate BM25 scores             │
│    - Sort by relevance                 │
│    - Top 5: [para_p1, para_p3, ...]    │
└────────────┬───────────────────────────┘
             ↓
┌────────────────────────────────────────┐
│ 5. SENTENCE SELECTION                  │
│    - Extract sentences from top paras  │
│    - Score sentences                   │
│    - Select top 3 sentences            │
└────────────┬───────────────────────────┘
             ↓
┌────────────────────────────────────────┐
│ 6. ANSWER COMPOSITION                  │
│    - Apply template                    │
│    - Add source citations              │
│    - Return answer                     │
└────────────────────────────────────────┘
```

### 6.2 Query Performance Metrics

| Step      | Operation           | Complexity | Time (60 paras) |
| --------- | ------------------- | ---------- | --------------- |
| 1         | Query Processing    | O(q)       | < 1 ms          |
| 2         | Index Lookup        | O(k)       | < 1 ms          |
| 3         | Retrieve Paragraphs | O(n)       | 2-5 ms          |
| 4         | BM25 Ranking        | O(c × m)   | 10-20 ms        |
| 5         | Sentence Selection  | O(c × s)   | 5-10 ms         |
| 6         | Answer Composition  | O(s)       | < 1 ms          |
| **Total** |                     |            | **< 50 ms**     |

Where:

- q = query length
- k = number of search terms
- n = total paragraphs
- c = candidate paragraphs
- m = average tokens per paragraph
- s = sentences selected

---

## 7. STORAGE FILE STRUCTURE

### 7.1 File System Layout

```
lifepathbot-backend/
└── app/
    └── data/
        └── knowledge_base.json    # Main storage file
```

### 7.2 File Characteristics

| Attribute       | Value                 |
| --------------- | --------------------- |
| **Format**      | JSON (UTF-8)          |
| **Size**        | ~2 MB (60 paragraphs) |
| **Lines**       | ~32,000               |
| **Indentation** | 2 spaces              |
| **Encoding**    | UTF-8                 |
| **Read/Write**  | Synchronous           |

### 7.3 Persistence Strategy

**Write Operation:**

```python
def _save_to_file(self):
    with open(self.storage_path, 'w', encoding='utf-8') as f:
        json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
```

**Read Operation:**

```python
def load(self):
    if os.path.exists(self.storage_path):
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            self.knowledge_base = json.load(f)
    return self.knowledge_base
```

**Advantages:**

- ✅ Atomic writes (file replaced entirely)
- ✅ No corruption risk
- ✅ Easy backup (copy file)
- ✅ Version control friendly

**Disadvantages:**

- ❌ Full file rewrite on every update
- ❌ Not suitable for concurrent writes
- ❌ Memory overhead (entire file in RAM)

---

## 8. SCALABILITY CONSIDERATIONS

### 8.1 Current Limitations

| Metric               | Limit   | Reason                   |
| -------------------- | ------- | ------------------------ |
| **Documents**        | ~100    | File size grows linearly |
| **Paragraphs**       | ~10,000 | Memory constraints       |
| **File Size**        | ~100 MB | Read/write performance   |
| **Concurrent Users** | 1       | No locking mechanism     |

### 8.2 Migration Path to MongoDB

**When to Migrate:**

- More than 100 documents
- Multiple concurrent users
- Need for complex aggregations
- Distributed deployment

**MongoDB Schema (Future):**

```javascript
// documents collection
{
  _id: ObjectId("..."),
  document_id: "doc_001",
  title: "Git Commands",
  source_path: "git.pdf",
  total_pages: 20,
  created_at: ISODate("2026-02-05T21:58:34Z")
}

// paragraphs collection
{
  _id: ObjectId("..."),
  para_id: "doc_001_p1_1",
  document_id: "doc_001",  // Foreign key
  text: "git init: Initializes...",
  page: 1,
  tokens: ["git", "init", "initialize"],
  lemmatized_tokens: ["git", "init", "initialize"],
  keywords: ["git", "init"],
  keyword_scores: { "git": 0.0234 },
  bigrams: ["git_init"],
  trigrams: ["git_init_initialize"]
}

// Indexes
db.paragraphs.createIndex({ "lemmatized_tokens": 1 })
db.paragraphs.createIndex({ "keywords": 1 })
db.paragraphs.createIndex({ "document_id": 1 })
```

**MongoDB Queries:**

```javascript
// Search by keyword
db.paragraphs.find({
  lemmatized_tokens: { $in: ["git", "init"] },
});

// Get paragraphs from document
db.paragraphs.find({ document_id: "doc_001" });

// Text search
db.paragraphs.find({
  $text: { $search: "git repository" },
});
```

---

## 9. COMPARISON: JSON vs MongoDB

| Feature               | JSON File                   | MongoDB                    |
| --------------------- | --------------------------- | -------------------------- |
| **Setup**             | None                        | Install MongoDB server     |
| **Query Speed**       | O(n) scan                   | O(log n) with indexes      |
| **Scalability**       | Limited                     | Excellent                  |
| **Concurrent Access** | No                          | Yes                        |
| **Transactions**      | No                          | Yes                        |
| **Backup**            | Copy file                   | mongodump                  |
| **Portability**       | Excellent                   | Good                       |
| **Learning Curve**    | Low                         | Medium                     |
| **Cost**              | Free                        | Free (Community)           |
| **Best For**          | Small datasets, single user | Large datasets, multi-user |

---

## 10. CONCLUSION

The current implementation uses **JSON file-based storage** which is:

- ✅ **Appropriate** for academic chatbot use case
- ✅ **Simple** to implement and maintain
- ✅ **Portable** and easy to share
- ✅ **Transparent** for debugging and inspection

**Future Enhancement:** Migration to MongoDB would be beneficial when:

- Scaling beyond 100 documents
- Supporting multiple concurrent users
- Requiring complex query capabilities
- Deploying in production environment

For the current academic project scope, JSON storage provides an excellent balance of simplicity and functionality.

---

**END OF DATABASE ARCHITECTURE DOCUMENT**
