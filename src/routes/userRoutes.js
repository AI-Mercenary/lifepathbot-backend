import express from 'express';
import { syncUser, updateProfile, getAllUsers } from '../controllers/userController.js';

const router = express.Router();

router.post('/sync', syncUser);
router.put('/profile', updateProfile);
router.get('/', getAllUsers);

export default router;
