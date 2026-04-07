# COMPLETE DATABASE ARCHITECTURE

## Dual-Backend System for Academic Chatbot Platform

---

## SYSTEM OVERVIEW

This project uses a **dual-backend architecture** with two separate storage systems:

1. **MongoDB** (Node.js/Express Backend) - User management & community features
2. **JSON File Storage** (Python/Streamlit Backend) - NLP knowledge base

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND APPLICATION                      │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
             ▼                                ▼
┌────────────────────────┐      ┌────────────────────────────┐
│  Node.js/Express API   │      │  Python/Streamlit API      │
│  (Port 5000)           │      │  (Port 8501)               │
│                        │      │                            │
│  - User Management     │      │  - Document Processing     │
│  - Suggestions         │      │  - Question Answering      │
│  - Authentication      │      │  - NLP Pipeline            │
└────────────┬───────────┘      └────────────┬───────────────┘
             │                                │
             ▼                                ▼
┌────────────────────────┐      ┌────────────────────────────┐
│      MONGODB           │      │    JSON FILE STORAGE       │
│  (Cloud/Local)         │      │  knowledge_base.json       │
│                        │      │                            │
│  - users-db collection │      │  - Documents               │
│  - suggestions         │      │  - Paragraphs              │
│                        │      │  - Inverted Index          │
└────────────────────────┘      └────────────────────────────┘
```

---

## PART 1: MONGODB DATABASE (Node.js Backend)

### 1.1 Database Connection

**File:** `src/config/db.js`

```javascript
import mongoose from "mongoose";

const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGO_URI);
    console.log(`MongoDB Connected: ${conn.connection.host}`);
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
};

export default connectDB;
```

**Environment Variable:**

```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/lifepathbot?retryWrites=true&w=majority
```

---

### 1.2 MongoDB Schema Design

#### Collection 1: `users-db`

**Purpose:** Store user profiles and authentication data

**Schema:** `src/models/User.js`

```javascript
const userSchema = new mongoose.Schema(
  {
    firebaseUid: {
      type: String,
      required: true,
      unique: true,
    },
    name: {
      type: String,
      required: true,
    },
    email: {
      type: String,
      required: true,
      unique: true,
    },
    student_id: String,
    age: Number,
    dept: String,
    specialization: String,
    role: {
      type: String,
      enum: ["student", "admin", "verified"],
      default: "student",
    },
    preferences: {
      notifications: { type: String, default: "app" },
      examMode: { type: Boolean, default: false },
      wakeTime: String,
      sleepTime: String,
    },
    createdAt: {
      type: Date,
      default: Date.now,
    },
  },
  { collection: "users-db" },
);
```

**Fields Explanation:**

| Field            | Type   | Required | Purpose                             |
| ---------------- | ------ | -------- | ----------------------------------- |
| `firebaseUid`    | String | Yes      | Firebase authentication ID (unique) |
| `name`           | String | Yes      | User's full name                    |
| `email`          | String | Yes      | User's email (unique)               |
| `student_id`     | String | No       | Student ID number                   |
| `age`            | Number | No       | User's age                          |
| `dept`           | String | No       | Department/Faculty                  |
| `specialization` | String | No       | Field of study                      |
| `role`           | String | Yes      | User role (student/admin/verified)  |
| `preferences`    | Object | No       | User preferences                    |
| `createdAt`      | Date   | Yes      | Account creation timestamp          |

**Indexes:**

```javascript
// Automatic indexes created by Mongoose
firebaseUid: unique index
email: unique index
```

---

#### Collection 2: `suggestions`

**Purpose:** Store community suggestions and discussions

**Schema:** `src/models/Suggestion.js`

```javascript
const suggestionSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "User",
    required: true,
  },
  authorName: String,
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  category: {
    type: String,
    enum: [
      "Hackathons",
      "hackathons",
      "Academics",
      "academics",
      "Courses",
      "courses",
      "Internships",
      "internships",
      "Careers",
      "careers",
      "Projects",
      "projects",
      "Tips & Tricks",
      "tips",
      "Tips",
      "General",
      "general",
    ],
    required: true,
    default: "General",
  },
  tags: [String],
  status: {
    type: String,
    enum: ["pending", "approved", "rejected"],
    default: "pending",
  },
  upvotes: {
    type: Number,
    default: 0,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});
```

**Fields Explanation:**

| Field         | Type     | Required | Purpose                                     |
| ------------- | -------- | -------- | ------------------------------------------- |
| `userId`      | ObjectId | Yes      | Reference to User who created suggestion    |
| `authorName`  | String   | No       | Cached author name for display              |
| `title`       | String   | Yes      | Suggestion title                            |
| `description` | String   | Yes      | Detailed description                        |
| `category`    | String   | Yes      | Category (Hackathons, Academics, etc.)      |
| `tags`        | Array    | No       | Tags for filtering                          |
| `status`      | String   | Yes      | Approval status (pending/approved/rejected) |
| `upvotes`     | Number   | Yes      | Number of upvotes                           |
| `createdAt`   | Date     | Yes      | Creation timestamp                          |

**Relationships:**

- `userId` → References `users-db._id` (Many-to-One)

---

### 1.3 MongoDB CRUD Operations

#### Create Operations

**Create User:**

```javascript
// POST /api/users
const newUser = await User.create({
  firebaseUid: "firebase_uid_123",
  name: "John Doe",
  email: "john@example.com",
  role: "student",
});
```

**Create Suggestion:**

```javascript
// POST /api/suggestions
const newSuggestion = await Suggestion.create({
  userId: user._id,
  authorName: user.name,
  title: "New Hackathon Opportunity",
  description: "Check out this amazing hackathon...",
  category: "Hackathons",
  tags: ["AI", "ML"],
});
```

---

#### Read Operations

**Get User by Firebase UID:**

```javascript
// GET /api/users/:firebaseUid
const user = await User.findOne({ firebaseUid: req.params.firebaseUid });
```

**Get All Approved Suggestions:**

```javascript
// GET /api/suggestions?status=approved
const suggestions = await Suggestion.find({ status: "approved" })
  .populate("userId", "name email")
  .sort({ createdAt: -1 });
```

**Get Suggestions by Category:**

```javascript
// GET /api/suggestions?category=Hackathons
const suggestions = await Suggestion.find({
  category: { $in: ["Hackathons", "hackathons"] },
  status: "approved",
});
```

**Get User's Suggestions:**

```javascript
// GET /api/suggestions/user/:userId
const userSuggestions = await Suggestion.find({
  userId: req.params.userId,
}).sort({ createdAt: -1 });
```

---

#### Update Operations

**Update User Profile:**

```javascript
// PUT /api/users/:id
const updatedUser = await User.findByIdAndUpdate(
  req.params.id,
  {
    dept: "Computer Science",
    specialization: "AI/ML",
    preferences: {
      notifications: "email",
      examMode: true,
    },
  },
  { new: true },
);
```

**Upvote Suggestion:**

```javascript
// PUT /api/suggestions/:id/upvote
const suggestion = await Suggestion.findByIdAndUpdate(
  req.params.id,
  { $inc: { upvotes: 1 } },
  { new: true },
);
```

**Approve/Reject Suggestion (Admin):**

```javascript
// PUT /api/suggestions/:id/status
const suggestion = await Suggestion.findByIdAndUpdate(
  req.params.id,
  { status: "approved" },
  { new: true },
);
```

---

#### Delete Operations

**Delete Suggestion:**

```javascript
// DELETE /api/suggestions/:id
await Suggestion.findByIdAndDelete(req.params.id);
```

---

### 1.4 MongoDB Indexes

**Automatic Indexes (Mongoose):**

```javascript
// User collection
_id: ObjectId (primary key, automatic)
firebaseUid: unique index
email: unique index

// Suggestion collection
_id: ObjectId (primary key, automatic)
userId: index (for foreign key lookups)
```

**Recommended Custom Indexes:**

```javascript
// For faster queries
db.suggestions.createIndex({ status: 1, createdAt: -1 });
db.suggestions.createIndex({ category: 1, status: 1 });
db.suggestions.createIndex({ userId: 1, createdAt: -1 });
```

---

### 1.5 MongoDB Query Examples

**Complex Query 1: Get Top Suggestions**

```javascript
const topSuggestions = await Suggestion.find({ status: "approved" })
  .sort({ upvotes: -1, createdAt: -1 })
  .limit(10)
  .populate("userId", "name dept");
```

**Complex Query 2: Search Suggestions**

```javascript
const results = await Suggestion.find({
  status: "approved",
  $or: [
    { title: { $regex: searchTerm, $options: "i" } },
    { description: { $regex: searchTerm, $options: "i" } },
    { tags: { $in: [searchTerm] } },
  ],
});
```

**Complex Query 3: User Statistics**

```javascript
const stats = await Suggestion.aggregate([
  { $match: { userId: mongoose.Types.ObjectId(userId) } },
  {
    $group: {
      _id: "$status",
      count: { $sum: 1 },
      totalUpvotes: { $sum: "$upvotes" },
    },
  },
]);
```

---

## PART 2: JSON FILE STORAGE (Python Backend)

### 2.1 Storage Location

**File:** `app/data/knowledge_base.json`  
**Format:** UTF-8 encoded JSON  
**Size:** ~2 MB (for 60 paragraphs)

---

### 2.2 JSON Schema Structure

```json
{
  "metadata": {
    "last_updated": "ISO 8601 timestamp",
    "total_documents": "integer",
    "total_paragraphs": "integer"
  },
  "documents": [
    {
      "document_id": "string",
      "title": "string",
      "source_path": "string",
      "total_pages": "integer",
      "paragraph_count": "integer"
    }
  ],
  "paragraphs": [
    {
      "para_id": "string",
      "text": "string",
      "page": "integer",
      "tokens": ["array"],
      "lemmatized_tokens": ["array"],
      "keywords": ["array"],
      "keyword_scores": {"object"},
      "bigrams": ["array"],
      "trigrams": ["array"]
    }
  ],
  "inverted_index": {
    "index": {
      "term": ["para_ids"]
    },
    "ngram_index": {
      "ngram": ["para_ids"]
    }
  }
}
```

---

### 2.3 JSON CRUD Operations

**Create (Add Document):**

```python
def save_document(self, document_data, inverted_index):
    self.knowledge_base["documents"].append(doc_metadata)
    self.knowledge_base["paragraphs"].extend(document_data["paragraphs"])
    self.knowledge_base["inverted_index"] = inverted_index.to_dict()
    self._save_to_file()
```

**Read (Query Paragraphs):**

```python
def get_paragraphs_by_ids(self, para_ids):
    return [p for p in self.knowledge_base["paragraphs"]
            if p["para_id"] in para_ids]
```

**Update (Metadata):**

```python
def update_metadata(self):
    self.knowledge_base["metadata"]["last_updated"] = datetime.now().isoformat()
    self._save_to_file()
```

**Delete (Clear All):**

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

---

## PART 3: INTEGRATION & DATA FLOW

### 3.1 Complete User Journey

```
1. User Registration (MongoDB)
   ↓
   POST /api/users → Create user in MongoDB

2. User Login (MongoDB)
   ↓
   GET /api/users/:firebaseUid → Fetch user profile

3. Upload PDF (JSON)
   ↓
   Process PDF → Extract text → Store in knowledge_base.json

4. Ask Question (JSON)
   ↓
   Query knowledge_base.json → Return answer

5. Post Suggestion (MongoDB)
   ↓
   POST /api/suggestions → Create suggestion in MongoDB

6. View Suggestions (MongoDB)
   ↓
   GET /api/suggestions → Fetch from MongoDB
```

### 3.2 Why Two Databases?

| Aspect               | MongoDB                       | JSON                    |
| -------------------- | ----------------------------- | ----------------------- |
| **Data Type**        | Structured user data          | Unstructured NLP data   |
| **Access Pattern**   | Multi-user, concurrent        | Single-user, read-heavy |
| **Query Complexity** | Complex (joins, aggregations) | Simple (keyword lookup) |
| **Update Frequency** | High (user actions)           | Low (document uploads)  |
| **Scalability Need** | High                          | Medium                  |
| **Technology**       | Node.js/Express               | Python/Streamlit        |

---

## PART 4: DATABASE COMPARISON

| Feature               | MongoDB               | JSON File          |
| --------------------- | --------------------- | ------------------ |
| **Setup**             | Cloud/Local server    | No setup           |
| **Query Speed**       | O(log n) with indexes | O(n) scan          |
| **Concurrent Access** | Yes                   | No                 |
| **Transactions**      | Yes                   | No                 |
| **Scalability**       | Excellent             | Limited            |
| **Best For**          | User management       | NLP knowledge base |

---

## PART 5: ENVIRONMENT CONFIGURATION

### MongoDB Connection String

```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/lifepathbot
```

### JSON Storage Path

```python
STORAGE_PATH = "app/data/knowledge_base.json"
```

---

## CONCLUSION

This dual-database architecture provides:

✅ **MongoDB** for scalable user management and community features  
✅ **JSON** for simple, portable NLP knowledge storage  
✅ **Separation of concerns** between user data and document data  
✅ **Technology-appropriate** storage for each backend

---

**END OF COMPLETE DATABASE ARCHITECTURE**
