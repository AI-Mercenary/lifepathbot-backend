import mongoose from 'mongoose';

const suggestionAnswerSchema = new mongoose.Schema({
  firebaseUid: String,
  authorName: String,
  text: { type: String, required: true },
  upvotes: { type: Number, default: 0 },
  createdAt: { type: Date, default: Date.now }
});

const suggestionSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: false
  },
  authorName: String, // Snapshot of name for easier display
  branch: { type: String, default: "General" },
  year: { type: String, default: "1" },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  category: {
    type: String,
    required: true,
    default: 'academics'
  },
  tags: [String],
  status: {
    type: String,
    enum: ['pending', 'approved', 'rejected'],
    default: 'pending'
  },
  upvotes: {
    type: Number,
    default: 0
  },
  answers: [suggestionAnswerSchema],
  createdAt: {
    type: Date,
    default: Date.now
  }
});

const Suggestion = mongoose.model('Suggestion', suggestionSchema);

export default Suggestion;
