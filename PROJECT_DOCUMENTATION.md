# LifePathBot — Complete Project Documentation

> An AI-powered peer-mentorship and academic guidance platform for students.
> Built for review-readiness with a clear module breakdown of both frontend and backend.

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Architecture Diagram](#3-architecture-diagram)
4. [Frontend Documentation](#4-frontend-documentation)
   - [Pages / Screens](#41-pages--screens)
   - [State & API Layer](#42-state--api-layer)
   - [Component System](#43-component-system)
   - [Routing & Deployment Config](#44-routing--deployment-config)
5. [Backend Documentation](#5-backend-documentation)
   - [Entry Point](#51-entry-point--serverjs)
   - [Routing Module](#52-routing-module-srcroutesr)
   - [Controller Module (AI & Logic)](#53-controller-module-srccontrollers)
   - [Database Schema Module](#54-database-schema-module-srcmodels)
   - [Config Module](#55-config-module-srcconfig)
6. [API Reference](#6-api-reference)
7. [Features](#7-features)
8. [Environment Variables](#8-environment-variables)
9. [Deployment Guide](#9-deployment-guide)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Project Overview

LifePathBot is a full-stack web application that provides students with:
- **AI Chat Assistant** — A dual-mode chatbot (General Mode & Study Mode) powered by the Groq API.
- **Community Hub (Suggestions)** — A peer-driven advice board where seniors share guidance on domains (Hackathons, Placements, Internships, etc.).
- **Goal & Reflection Tracking** — Students can set SMART goals and log daily reflections.
- **Admin Dashboard** — Admins moderate suggestions, view users, monitor chat logs, and bulk-import suggestions from Google Forms CSV/XLSX exports.

| Attribute | Value |
|---|---|
| Frontend URL | https://lifepath-bot.vercel.app |
| Backend URL | https://lifepathbot-backend-ai-mercenary5381-vc27i7u0.leapcell.dev |
| Frontend Repo | `AI-Mercenary/lifepathbot-frontend` |
| Backend Repo | `AI-Mercenary/lifepathbot-backend` |

---

## 2. Tech Stack

### Frontend
| Layer | Technology |
|---|---|
| Framework | React + Vite (TypeScript) |
| Styling | Tailwind CSS + shadcn/ui |
| State Management | React Context API |
| Auth | Firebase Authentication (Google + Email/Password) |
| Icons | Lucide React + MUI Icons |
| HTTP | Native `fetch` API |
| Hosting | Vercel |

### Backend
| Layer | Technology |
|---|---|
| Runtime | Node.js (ES Modules) |
| Framework | Express.js |
| AI Engine | Groq API (`llama-3.3-70b-versatile`) |
| Database | MongoDB Atlas via Mongoose |
| Auth Verification | Firebase Admin SDK |
| File Parsing | `pdfjs-dist`, `xlsx` |
| Real-time | Socket.io |
| Hosting | Leapcell |

---

## 3. Architecture Diagram

```
┌──────────────────────────────────┐
│        Vercel (Frontend)         │
│  React + Vite + shadcn/ui        │
│                                  │
│  Pages: Chat, Suggestions,       │
│         Dashboard, Admin         │
│                                  │
│  AppContext → api/*.ts ──────────┼──── HTTPS/JSON ─────┐
└──────────────────────────────────┘                      │
                                                          ▼
                                         ┌─────────────────────────────┐
                                         │   Leapcell (Backend)        │
                                         │   Express.js Server         │
                                         │                             │
                                         │   Routes → Controllers      │
                                         │       ↓           ↓         │
                                         │   Groq API    MongoDB Atlas │
                                         └─────────────────────────────┘
                                                    ↑
                                         Firebase Auth (token verify)
```

---

## 4. Frontend Documentation

**Local Path:** `e:\lifepathbot-frontend`
**Entry:** `src/main.tsx` → `src/App.tsx`

### 4.1 Pages / Screens

Located in `src/pages/`:

#### `Chat.tsx` — AI Chat Interface
- Renders the core dual-mode chatbot screen.
- **General Mode**: Feeds recent goals, reflections, and peer suggestions as context to the AI.
- **Study Mode**: Accepts PDF/DOCX/PPT uploads, parses them via the backend, and allows the student to ask questions about the material.
- Features a persistent **left sidebar** with session history, selectable past chats, and a delete option.
- **Session management**: Each conversation has a unique `sessionId` (timestamped) saved to MongoDB for continuity.
- The "Synthesizing..." animation renders while the Groq API is processing.
- **Key components used**: `ScrollArea`, `Badge`, `Select`, `Input`, `Button`.
- **Key API calls**: `askChatbot()`, `saveChatMessage()`, `getUserSessions()`, `uploadMaterial()`.

#### `Suggestions.tsx` — Community Hub
- Displays approved peer suggestions in a **clean vertical stacked layout** (not a grid).
- Each suggestion card shows: **Author name**, **Branch + Year**, **Category badge**, and the **suggestion body**.
- Long suggestions are truncated to 3 lines with a **"Read More..."** toggle that expands inline.
- Bulk-uploaded suggestions (from CSV) suppress the auto-generated title to avoid visual duplication.
- **Voting**: Each user is limited to **1 vote per suggestion** (tracked in local state by suggestion ID).
- Submit dialog allows logged-in students to post new suggestions (pending admin approval).
- **Filter bar**: Clickable pill buttons to filter by category (Hackathons, Placements, Academics, etc.).
- **Key API calls**: `getSuggestions()`, `createSuggestion()`.

#### `AdminDashboard.tsx` — Admin Control Panel
- Protected route, visible only to admin users.
- **Tabs**: Users, Chat Logs, Pending Suggestions, Content Moderation, Bulk Upload.
- **Bulk Upload**: Accepts `.csv` or `.xlsx` files from Google Forms exports. Parses specific columns:

  | CSV Column | Mapped To |
  |---|---|
  | `Name` | `authorName` |
  | `Department` | `branch` |
  | `Year of Study` | `year` |
  | `What type of guidance...` | `category` |
  | `Your detailed suggestion/guidance` | `description` |

- Admins can **Approve** or **Reject** pending suggestions.
- **Key API calls**: `bulkCreateSuggestions()`, `getSuggestions('pending')`, `approveSuggestion()`, `rejectSuggestion()`.

#### `Dashboard.tsx`, `Goals.tsx`, `Reflections.tsx`
- Student-facing pages for tracking personal SMART goals and daily mood/accomplishment reflections.
- Goals have a visual progress bar and completion toggle.
- Reflections let students log mood and key accomplishments for the day.

---

### 4.2 State & API Layer

#### `src/context/AppContext.tsx` — Global State (Central Nervous System)
- Wraps the entire app.
- Manages: `user` (Firebase profile + MongoDB sync), `goals`, `reflections`, `chatHistory`.
- On login, calls `/api/users/sync` to upsert the Firebase user into MongoDB.

#### `src/api/` — Network Bridge Module
Each file is a thin wrapper around `fetch` pointing to `VITE_API_URL`:

| File | Exports |
|---|---|
| `chat.ts` | `askChatbot`, `saveChatMessage`, `getUserSessions`, `getSessionMessages`, `deleteChatSession`, `uploadMaterial` |
| `suggestions.ts` | `getSuggestions`, `createSuggestion`, `bulkCreateSuggestions`, `approveSuggestion`, `rejectSuggestion` |
| `users.ts` | `syncUser`, `getAllUsers` |
| `goals.ts` | `getGoals`, `createGoal`, `updateGoal`, `deleteGoal` |
| `reflections.ts` | `getReflections`, `createReflection` |

---

### 4.3 Component System

Located in `src/components/`. Uses **shadcn/ui** for consistency:

| Component | Purpose |
|---|---|
| `ui/button.tsx` | Standardized button with variants (default, outline, ghost) |
| `ui/card.tsx` | Container card used across all pages |
| `ui/dialog.tsx` | Modal overlays (Submit Suggestion, etc.) |
| `ui/badge.tsx` | Category/status labels |
| `ui/scroll-area.tsx` | Custom scrollable containers |
| `ui/select.tsx` | Dropdown selects (mode switcher, category picker) |
| `ThemeToggle.tsx` | Dark/Light mode toggle |

---

### 4.4 Routing & Deployment Config

#### `src/App.tsx`
- Uses `react-router-dom` for client-side routing.
- Routes: `/`, `/login`, `/dashboard`, `/chat`, `/suggestions`, `/goals`, `/reflections`, `/admin`.

#### `vercel.json` — Fixes Client-Side Routing 404s
```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```
Without this, refreshing `/chat` on Vercel returns a `404: NOT_FOUND` because Vercel treats it as a static file path. This rewrite routes all requests through the React app.

---

## 5. Backend Documentation

**Local Path:** `e:\lifepathbot-backend`
**Entry:** `server.js`

### 5.1 Entry Point — `server.js`

- Initializes Express, Socket.io, CORS, and connects to MongoDB.
- **CORS config**: Uses `origin: true` (dynamic reflection) to support any origin — critical for Vercel ↔ Leapcell communication.
- **Health check**: `GET /api/health` — returns server status and active endpoints. Used to verify deployment.
- Registers all route modules.
- Binds to `process.env.PORT` (managed by Leapcell dynamically).

---

### 5.2 Routing Module (`src/routes/`)

Acts as the URL switchboard — maps incoming API requests to the right controller function.

| Route File | Prefix | Purpose |
|---|---|---|
| `chatRoutes.js` | `/api/chat` | Chat sessions, history, AI ask, PDF upload |
| `suggestionRoutes.js` | `/api/suggestions` | Get, create, bulk create, approve/reject |
| `userRoutes.js` | `/api/users` | Sync Firebase user, get all users |
| `goalRoutes.js` | `/api/goals` | CRUD for student goals |
| `reflectionRoutes.js` | `/api/reflections` | CRUD for daily reflections |
| `questionRoutes.js` | `/api/questions` | Community Q&A |

---

### 5.3 Controller Module (`src/controllers/`)

The "Brain" — contains all business logic.

#### `chatController.js` — AI & RAG Engine
- **`askAI(req, res)`**: Core AI function.
  1. Receives `{ message, context }` from the frontend.
  2. Builds a structured system prompt including user profile, goals, reflections, and peer suggestions.
  3. Calls the **Groq API** (`groq.chat.completions.create`) with `llama-3.3-70b-versatile`.
  4. Returns the AI's response text to the frontend via JSON.
- **`uploadMaterial(req, res)`**: PDF/document RAG handler.
  1. Receives the uploaded file via `multer` (stored in memory, not on disk).
  2. Parses text from PDF using `pdfjs-dist` (or raw buffer for other formats).
  3. Chunks the text and stores it in a temporary in-memory map keyed to the session.
  4. Subsequent `/ask` calls inject this chunked text as additional context.
- **`getSessions`, `getSessionMessages`, `deleteSession`**: CRUD for persisted chat sessions in MongoDB.

#### `suggestionController.js` — Suggestion Logic
- **`bulkCreate(req, res)`**: Accepts an array of suggestion objects from the Admin Dashboard's CSV parser. Bulk-inserts them into MongoDB with `status: 'pending'`.
- **`approveSuggestion`**: Updates `status` to `'approved'` so it appears publicly.
- **`getSuggestions`**: Returns suggestions filtered by status (defaults to `'approved'` for public view).

#### `userController.js`
- **`syncUser`**: Upserts a user from Firebase into MongoDB on every login. Creates the record if new, updates `name`/`email` if existing.
- **`getAllUsers`**: Returns all registered users for the Admin Dashboard.

---

### 5.4 Database Schema Module (`src/models/`)

All schemas defined with Mongoose. Every document gets `createdAt`/`updatedAt` via `{ timestamps: true }`.

#### `User.js`
```js
{
  firebaseUid: String (unique, required),
  name: String,
  email: String,
  role: String (default: 'student'),
  branch: String,
  year: String,
  profilePic: String
}
```

#### `Suggestion.js`
```js
{
  firebaseUid: String,
  authorName: String,
  title: String,
  description: String (required),
  category: String,
  branch: String,
  year: String,
  tags: [String],
  upvotes: Number (default: 0),
  status: String (default: 'pending')  // 'pending' | 'approved' | 'rejected'
}
```

#### `Chat.js`
```js
{
  firebaseUid: String,
  userName: String,
  sessionId: String,
  role: String,       // 'user' | 'bot'
  text: String,
  agentType: String   // 'general' | 'study'
}
```

#### `Goal.js`
```js
{
  firebaseUid: String,
  title: String,
  description: String,
  progress: Number (0–100),
  completed: Boolean
}
```

#### `Reflection.js`
```js
{
  firebaseUid: String,
  mood: String,
  accomplishments: String,
  challenges: String,
  nextSteps: String
}
```

---

### 5.5 Config Module (`src/config/`)

#### `db.js` — MongoDB Connection
- Uses `mongoose.connect(process.env.MONGO_URI)`.
- **Does NOT call `process.exit(1)` on failure** — this was intentionally removed to prevent Leapcell containers from crashing. Instead, it logs the error and allows the health check endpoint to remain accessible.

---

## 6. API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Server health check |
| POST | `/api/users/sync` | Firebase → MongoDB user sync |
| GET | `/api/users` | Get all users (admin) |
| POST | `/api/chat/ask` | Send message, get AI response |
| POST | `/api/chat/upload-material` | Upload study PDF/doc |
| GET | `/api/chat/sessions/:uid` | Get all chat sessions for a user |
| GET | `/api/chat/sessions/:sessionId/messages` | Get all messages in a session |
| DELETE | `/api/chat/sessions/:sessionId` | Delete a session |
| GET | `/api/suggestions` | Get approved suggestions |
| POST | `/api/suggestions` | Create a new suggestion |
| POST | `/api/suggestions/bulk` | Bulk create (admin CSV upload) |
| PATCH | `/api/suggestions/:id/approve` | Approve a suggestion |
| PATCH | `/api/suggestions/:id/reject` | Reject a suggestion |
| GET | `/api/goals/:uid` | Get goals for a user |
| POST | `/api/goals` | Create a goal |
| PATCH | `/api/goals/:id` | Update goal progress |
| DELETE | `/api/goals/:id` | Delete a goal |
| GET | `/api/reflections/:uid` | Get reflections for a user |
| POST | `/api/reflections` | Create a reflection |

---

## 7. Features

### AI Chatbot (Dual-Mode)
- **General Mode**: Acts as a peer mentor. Pulls the student's goals, reflections, and community suggestions to give personalized, campus-aware guidance.
- **Study Mode**: Accepts file uploads (PDF, DOCX, PPT). Parses and stores text in memory. Answers questions grounded strictly in the uploaded material.
- AI model is fully white-labeled — no AI provider name is shown to students.

### Community Hub
- Students and seniors can submit peer suggestions by category.
- All submissions are **pending by default** — admins must approve before public display.
- Stacked vertical layout with truncated descriptions and inline **Read More** expansion.
- **1 vote per suggestion per user** (enforced on the frontend per session).

### Admin Dashboard
- **Bulk CSV/XLSX Import** from Google Forms exports.
- User management table.
- Suggestion moderation (approve/reject).
- Chat log viewer for monitoring AI interactions.

### Goal & Reflection Module
- Students set SMART goals with a progress slider (0–100%).
- Daily reflections capture mood, accomplishments, challenges, and next steps.
- Both modules feed context to the AI for more personalized responses.

---

## 8. Environment Variables

### Backend (Leapcell Dashboard)
| Variable | Description |
|---|---|
| `MONGO_URI` | MongoDB Atlas connection string |
| `GROQ_API_KEY` | Groq API authentication key |
| `PORT` | Managed automatically by Leapcell |

### Frontend (Vercel Dashboard)
| Variable | Description |
|---|---|
| `VITE_API_URL` | Full URL of the Leapcell backend |
| `VITE_FIREBASE_API_KEY` | Firebase project API key |
| `VITE_FIREBASE_AUTH_DOMAIN` | Firebase auth domain |
| `VITE_FIREBASE_PROJECT_ID` | Firebase project ID |

---

## 9. Deployment Guide

### Backend → Leapcell
1. Make code changes in `e:\lifepathbot-backend`.
2. Run:
   ```bash
   git add .
   git commit -m "your message"
   git push origin main
   ```
3. Go to the **Leapcell Dashboard** → click **Redeploy**.
4. Monitor the build logs. A healthy startup looks like:
   ```
   Server running on port 8080
   MongoDB connected
   ```

> ⚠️ **MongoDB Atlas Network Access**: You must whitelist `0.0.0.0/0` under **Security → Network Access** on MongoDB Atlas, or Leapcell's dynamic IP will be blocked, causing all `/api/*` routes to return `500`.

### Frontend → Vercel
1. Make code changes in `e:\lifepathbot-frontend`.
2. Run:
   ```bash
   git add .
   git commit -m "your message"
   git push origin main
   ```
3. Vercel **auto-deploys** within ~60 seconds. No manual trigger needed.
4. Hard-refresh your browser (`Ctrl + F5`) to clear cached assets.

---

## 10. Troubleshooting

| Symptom | Root Cause | Fix |
|---|---|---|
| `500 Internal Server Error` on all API calls | MongoDB Atlas blocking Leapcell IP | Whitelist `0.0.0.0/0` in Atlas Network Access |
| `404: NOT_FOUND` on page refresh in browser | Vercel treating React routes as file paths | Already fixed via `vercel.json` rewrites |
| `AI connection failed` toast in chat | Groq API key missing or backend crashed | Check Leapcell env vars and runtime logs |
| `auth/invalid-credential` on login | Wrong email/password entered | Use correct credentials or Google Sign-In |
| Bulk upload shows `No valid suggestions found` | CSV column names don't match expected headers | Ensure file uses exact Google Forms column names |
| Session badge showing raw numbers on chat screen | Old cached frontend build | Hard refresh (`Ctrl + F5`) to clear cache |
