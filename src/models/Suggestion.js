import mongoose from 'mongoose';

const suggestionSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  authorName: String, // Snapshot of name for easier display
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
    enum: [
      'Hackathons', 'hackathons',
      'Academics', 'academics',
      'Courses', 'courses',
      'Internships', 'internships',
      'Careers', 'careers',
      'Projects', 'projects',
      'Tips & Tricks', 'tips', 'Tips', // accommodating variations
      'General', 'general'
    ],
    required: true,
    default: 'General'
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
  createdAt: {
    type: Date,
    default: Date.now
  }
});

const Suggestion = mongoose.model('Suggestion', suggestionSchema);

export default Suggestion;
