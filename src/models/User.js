import mongoose from 'mongoose';

const userSchema = new mongoose.Schema({
  firebaseUid: {
    type: String,
    required: true,
    unique: true
  },
  name: {
    type: String,
    required: true
  },
  email: {
    type: String,
    required: true,
    unique: true
  },
  student_id: String,
  dept: String,
  year: { type: String, default: "1" },
  specialization: String,
  role: {
    type: String,
    enum: ['student', 'admin', 'verified'],
    default: 'student'
  },
  preferences: {
    notifications: { type: String, default: 'app' },
    examMode: { type: Boolean, default: false },
    wakeTime: String,
    sleepTime: String
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
}, { collection: 'users-db' });

const User = mongoose.model('User', userSchema);

export default User;
