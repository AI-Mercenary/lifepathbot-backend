import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import { createServer } from 'http';
import { Server } from 'socket.io';
import connectDB from './src/config/db.js';
import userRoutes from './src/routes/userRoutes.js';
import suggestionRoutes from './src/routes/suggestionRoutes.js';
import chatRoutes from './src/routes/chatRoutes.js';
import questionRoutes from './src/routes/questionRoutes.js';
import goalRoutes from './src/routes/goalRoutes.js';
import reflectionRoutes from './src/routes/reflectionRoutes.js';

// Load env vars
dotenv.config();

// Connect to Database
connectDB();

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "*", 
    methods: ["GET", "POST"],
    credentials: true
  }
});

// Middleware (Bulletproof CORS configuration)
app.use(cors({
  origin: true, // Dynamically reflects origin
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
  credentials: true,
  optionsSuccessStatus: 200 // Some legacy browsers and environments choke on 204
}));

app.use(express.json());

// Health Check
app.get('/api/health', (req, res) => {
  res.status(200).json({ 
    status: 'OK', 
    version: '1.2.session-support', 
    endpoints: ['/api/chat/sessions', '/api/chat/ask'] 
  });
});

// Routes
app.use('/api/users', userRoutes);
app.use('/api/suggestions', suggestionRoutes);
app.use('/api/chat', chatRoutes);
app.use('/api/questions', questionRoutes);
app.use('/api/goals', goalRoutes);
app.use('/api/reflections', reflectionRoutes);

app.get('/', (req, res) => {
  res.send('LifePathBot Backend Running');
});

// Socket.io
io.on('connection', (socket) => {
  console.log('User connected', socket.id);
  socket.on('disconnect', () => {
    console.log('User disconnected', socket.id);
  });
});

const PORT = process.env.PORT || 5000;

httpServer.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
