import express from 'express';
import { syncUser, updateProfile } from '../controllers/userController.js';

const router = express.Router();

router.post('/sync', syncUser);
router.put('/profile', updateProfile);

export default router;
