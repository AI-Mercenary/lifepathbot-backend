import Suggestion from '../models/Suggestion.js';
import User from '../models/User.js';

// @desc    Create a suggestion
// @route   POST /api/suggestions
// @access  Private
export const createSuggestion = async (req, res) => {
  const { firebaseUid, title, description, category, tags } = req.body;

  try {
    const user = await User.findOne({ firebaseUid });
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    const suggestion = await Suggestion.create({
      userId: user._id,
      authorName: user.name,
      branch: user.dept || 'General',
      year: user.year || '1',
      title,
      description,
      category,
      tags
    });

    res.status(201).json(suggestion);
  } catch (error) {
    console.error(error);
    res.status(400).json({ message: error.message });
  }
};

// @desc    Get all suggestions (with filters)
// @route   GET /api/suggestions
// @access  Public
export const getSuggestions = async (req, res) => {
  const { category, status } = req.query;
  const filter = {};
  
  if (category && category !== 'all') {
    // Case-insensitive match: matches 'Hackathons' or 'hackathons'
    filter.category = new RegExp(`^${category}$`, 'i');
  }
  if (status) filter.status = status;
  // Default to approved only for public view? Or pending for admin?
  // For now return all matching filters.

  try {
    const suggestions = await Suggestion.find(filter).sort({ createdAt: -1 });
    res.json(suggestions);
  } catch (error) {
    console.error("Get Suggestions Error:", error);
    res.status(500).json({ message: error.message, stack: error.stack });
  }
};

// @desc    Update suggestion status
// @route   PATCH /api/suggestions/:id/status
// @access  Admin
export const updateStatus = async (req, res) => {
  const { id } = req.params;
  const { status } = req.body;

  if (!['approved', 'rejected', 'pending'].includes(status)) {
      return res.status(400).json({ message: 'Invalid status' });
  }

  try {
      const suggestion = await Suggestion.findById(id);
      if (!suggestion) {
          return res.status(404).json({ message: 'Suggestion not found' });
      }

      suggestion.status = status;
      await suggestion.save();
      
      res.json(suggestion);
  } catch (error) {
      res.status(400).json({ message: error.message });
  }
};

// @desc    Bulk create suggestions
// @route   POST /api/suggestions/bulk
// @access  Admin
export const bulkCreateSuggestions = async (req, res) => {
  const suggestions = req.body;
  
  if (!Array.isArray(suggestions)) {
    return res.status(400).json({ message: 'Payload must be an array of suggestions' });
  }

  try {
    // Map status to approved by default for bulk admin uploads
    const dataToInsert = suggestions.map(s => ({
      ...s,
      status: 'approved'
    }));

    const result = await Suggestion.insertMany(dataToInsert, { ordered: false });
    res.status(201).json({ message: `${result.length} suggestions inserted`, data: result });
  } catch (error) {
    console.error("Bulk insert error:", error);
    res.status(500).json({ message: error.message, stack: error.stack });
  }
};
