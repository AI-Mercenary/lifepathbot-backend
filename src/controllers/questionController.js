import Question from '../models/Question.js';
import Suggestion from '../models/Suggestion.js';

// @desc    Create a new question
// @route   POST /api/questions
// @access  Public
export const createQuestion = async (req, res) => {
  const { firebaseUid, authorName, title, body, category, tags } = req.body;

  try {
    const question = await Question.create({
      firebaseUid,
      authorName: authorName || 'Anonymous',
      title,
      body,
      category,
      tags: tags || []
    });
    res.status(201).json(question);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
};

// @desc    Get all questions (with optional category filter)
// @route   GET /api/questions
// @access  Public
export const getQuestions = async (req, res) => {
  const { category, search } = req.query;
  let query = {};
  
  if (category && category !== 'all') {
    query.category = new RegExp(`^${category}$`, 'i');
  }
  
  if (search) {
      query.$or = [
          { title: { $regex: search, $options: 'i' } },
          { body: { $regex: search, $options: 'i' } }
      ];
  }

  try {
    const questions = await Question.find(query).lean();
    
    // Also fetch approved suggestions
    let suggestionQuery = { status: 'approved' };
    if (category && category !== 'all') {
      suggestionQuery.category = new RegExp(`^${category}$`, 'i');
    }
    if (search) {
      suggestionQuery.$or = [
          { title: { $regex: search, $options: 'i' } },
          { description: { $regex: search, $options: 'i' } }
      ];
    }
    const suggestions = await Suggestion.find(suggestionQuery).lean();

    // Normalize suggestions to look like questions for the frontend map
    const normalizedSuggestions = suggestions.map(s => ({
       ...s,
       body: s.description,
       _id: s._id,
       category: s.category.toLowerCase(),
       answers: s.answers || [],
       isSuggestion: true 
    }));

    // Merge and sort
    const combined = [...questions, ...normalizedSuggestions].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    res.json(combined);
  } catch (error) {
    console.error("Get Questions Error", error);
    res.status(500).json({ message: error.message });
  }
};

// @desc    Add an answer to a question
// @route   POST /api/questions/:id/answer
// @access  Public
export const answerQuestion = async (req, res) => {
  const { id } = req.params;
  const { firebaseUid, authorName, text } = req.body;

  try {
    let target = await Question.findById(id);
    let isSuggestion = false;

    if (!target) {
      target = await Suggestion.findById(id);
      isSuggestion = true;
    }

    if (!target) {
      return res.status(404).json({ message: 'Post not found' });
    }

    target.answers.push({
      firebaseUid,
      authorName: authorName || 'Anonymous',
      text
    });

    await target.save();
    res.status(201).json(target);
  } catch (error) {
    console.error("Answer Question Error", error);
    res.status(400).json({ message: error.message });
  }
};
