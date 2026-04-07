import mongoose from 'mongoose';

const reflectionSchema = new mongoose.Schema({
  firebaseUid: { type: String, required: true },
  date: String,
  accomplishments: String,
  challenges: String,
  mood: Number,
  productivity: Number,
  notes: String,
  createdAt: { type: Date, default: Date.now }
});

export default mongoose.model('Reflection', reflectionSchema);
