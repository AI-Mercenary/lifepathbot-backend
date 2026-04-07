import Reflection from '../models/Reflection.js';

export const getReflections = async (req, res) => {
  const { uid } = req.params;
  try {
    const reflections = await Reflection.find({ firebaseUid: uid }).sort({ createdAt: -1 });
    res.json(reflections);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

export const createReflection = async (req, res) => {
  try {
    const reflection = await Reflection.create(req.body);
    res.status(201).json(reflection);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
};
