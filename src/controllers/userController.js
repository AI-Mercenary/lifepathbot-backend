import User from '../models/User.js';

// @desc    Auth/Sync User
// @route   POST /api/users/sync
// @access  Public (protected by firebase check in frontend usually, typically we verify token here)
export const syncUser = async (req, res) => {
  const { firebaseUid, email, name, role } = req.body;

  try {
    let user = await User.findOne({ firebaseUid });

    if (user) {
      // Update existing user
      user.name = name || user.name;
      user.email = email || user.email;
      user.role = role || user.role;
      // Don't overwrite preferences or other fields blindly
      await user.save();
      return res.json(user);
    } 

    // Create new user
    user = await User.create({
      firebaseUid,
      name,
      email,
      role: role || 'student',
      student_id: '',
      dept: '', 
      specialization: '',
      age: null
    });

    res.status(201).json(user);
  } catch (error) {
    console.error("Sync User Error:", error);
    res.status(400).json({ message: error.message, stack: error.stack });
  }
};

// @desc    Update User Profile
// @route   PUT /api/users/profile
// @access  Private
export const updateProfile = async (req, res) => {
  const { firebaseUid, student_id, age, dept, specialization, year, branch } = req.body;

  try {
    const user = await User.findOne({ firebaseUid });

    if (user) {
      user.student_id = student_id || user.student_id;
      user.age = age || user.age;
      user.dept = dept || user.dept; // Note: Frontend uses 'branch', mapping needs care
      user.specialization = specialization || user.specialization;
      // Map frontend 'branch' to 'dept' if needed or store both. Schema has 'dept'.
      if (branch) user.dept = branch; 
      
      await user.save();
      res.json(user);
    } else {
      res.status(404).json({ message: 'User not found' });
    }
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
};
