import mongoose from 'mongoose';

const taskSchema = new mongoose.Schema({
  id: String,
  text: String,
  completed: Boolean,
  dueDate: String,
  createdAt: String
});

const goalSchema = new mongoose.Schema({
  firebaseUid: { type: String, required: true },
  title: { type: String, required: true },
  description: String,
  category: String,
  deadline: String,
  progress: { type: Number, default: 0 },
  tasks: [taskSchema],
  isCompleted: { type: Boolean, default: false },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

export default mongoose.model('Goal', goalSchema);
