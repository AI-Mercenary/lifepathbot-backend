import express from 'express';
import { createSuggestion, getSuggestions, updateStatus } from '../controllers/suggestionController.js';

const router = express.Router();

router.post('/', createSuggestion);
router.get('/', getSuggestions);
router.patch('/:id/status', updateStatus);

export default router;
