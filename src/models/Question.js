import mongoose from 'mongoose';

const answerSchema = new mongoose.Schema({
  firebaseUid: String,
  authorName: String,
  text: { type: String, required: true },
  upvotes: { type: Number, default: 0 },
  createdAt: { type: Date, default: Date.now }
});

const questionSchema = new mongoose.Schema({
  firebaseUid: { type: String, required: true },
  authorName: String,
  title: { type: String, required: true },
  body: String,
  category: {
    type: String,
    default: 'general'
  },
  tags: [String],
  upvotes: { type: Number, default: 0 },
  answers: [answerSchema],
  status: { type: String, enum: ['open', 'closed'], default: 'open' },
  createdAt: { type: Date, default: Date.now }
});

const Question = mongoose.model('Question', questionSchema);
export default Question;
