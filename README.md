# LifePathBot - AI-Powered Student Success Platform

LifePathBot is a comprehensive student life management application featuring an AI-powered chatbot (Study Mode & General Mode), goal tracking, daily reflections, and academic support.

## 🚀 Key Features

- **Study Mode**: Upload documents (.pdf, .docx, .pptx) and chat with them using strict RAG (Retrieval-Augmented Generation).
- **General Mode**: Daily companion for student suggestions, reflections, and goal setting.
- **Goal Management**: SMART goals with progress tracking and deadlines.
- **Daily Reflections**: Mood tracking and productivity logging.
- **Authentication**: Secure login using Firebase.
- **Responsive UI**: Modern, dark-themed dashboard built with React and Tailwind CSS.

---

## 🛠️ Tech Stack

- **Frontend**: React (Vite), TypeScript, Tailwind CSS, shadcn/ui.
- **Backend**: Node.js, Express, MongoDB (Mongoose).
- **AI**: Local LLM (Ollama with `llama3.2:1b`), Gemini API.
- **Auth**: Firebase Authentication.
- **Parsing**: `pdf-parse`, `officeparser`.

---

## 🏗️ Getting Started (A to Z Setup)

### 1. Prerequisites
- [Node.js](https://nodejs.org/) (v18+)
- [MongoDB](https://www.mongodb.com/) (Local or Atlas)
- [Ollama](https://ollama.com/) (For local AI)
- [Firebase Account](https://firebase.google.com/)

### 2. Setup Ollama (Local AI)
1. Download and install Ollama from [ollama.com](https://ollama.com/).
2. Open your terminal and pull the Llama 3.2 model:
   ```bash
   ollama pull llama3.2:1b
   ```
3. Keep Ollama running in the background.

### 3. Backend Setup
1. Clone the backend repository:
   ```bash
   git clone https://github.com/AI-Mercenary/lifepathbot-backend.git
   cd lifepathbot-backend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file in the root:
   ```env
   PORT=5000
   MONGO_URI=your_mongodb_connection_string
   FIREBASE_PROJECT_ID=your_firebase_project_id
   ```
4. Start the server:
   ```bash
   npm start
   ```

### 4. Frontend Setup
1. Clone the frontend repository:
   ```bash
   git clone https://github.com/AI-Mercenary/lifepath-bot-frontend.git
   cd lifepath-bot-frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file in the root:
   ```env
   VITE_FIREBASE_API_KEY=your_key
   VITE_FIREBASE_AUTH_DOMAIN=your_domain
   VITE_FIREBASE_PROJECT_ID=your_id
   VITE_FIREBASE_STORAGE_BUCKET=your_bucket
   VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   VITE_FIREBASE_APP_ID=your_app_id
   VITE_FIREBASE_MEASUREMENT_ID=your_measurement_id
   VITE_API_URL=http://localhost:5000/api
   ```
4. Start the development server:
   ```bash
   npm run dev
   ```

---

## 📖 Usage Guide

1. **Sign Up/Login**: Create an account using the authentication page.
2. **Dashboard**: View your current goals, mood trends, and reflections.
3. **Study Mode**:
   - Go to Chat -> Select **Study Mode** from the dropdown.
   - Click the **Upload** icon to attach a PDF, Word doc, or PowerPoint.
   - Ask questions related *only* to the document.
4. **General Mode**: Toggle to **General Mode** for habit tracking and motivation.
5. **Goal Tracking**: Add new goals and update progress as you complete them.

---

## 📄 License
MIT
