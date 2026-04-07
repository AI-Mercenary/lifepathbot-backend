import Goal from '../models/Goal.js';

export const getGoals = async (req, res) => {
  const { uid } = req.params;
  try {
    const goals = await Goal.find({ firebaseUid: uid }).sort({ createdAt: -1 });
    res.json(goals);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

export const createGoal = async (req, res) => {
  try {
    const goal = await Goal.create(req.body);
    res.status(201).json(goal);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
};

export const updateGoal = async (req, res) => {
  const { id } = req.params;
  try {
    const goal = await Goal.findByIdAndUpdate(id, { ...req.body, updatedAt: Date.now() }, { new: true });
    res.json(goal);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
};

export const deleteGoal = async (req, res) => {
  const { id } = req.params;
  try {
    await Goal.findByIdAndDelete(id);
    res.json({ message: 'Goal removed' });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};
