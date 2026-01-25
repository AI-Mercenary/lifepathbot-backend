import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import { createServer } from 'http';
import { Server } from 'socket.io';
import connectDB from './src/config/db.js';
import userRoutes from './src/routes/userRoutes.js';
import suggestionRoutes from './src/routes/suggestionRoutes.js';

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

// Middleware
// Middleware
const allowedOrigins = [
  'https://lifepath-bot.vercel.app', 
  'http://localhost:5173',
  'http://localhost:5000'
];

app.use(cors({
  origin: allowedOrigins,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
}));
app.use(express.json());

// Routes
app.use('/api/users', userRoutes);
app.use('/api/suggestions', suggestionRoutes);

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
