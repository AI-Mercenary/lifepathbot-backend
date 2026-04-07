import express from 'express';
import { createSuggestion, getSuggestions, updateStatus, bulkCreateSuggestions } from '../controllers/suggestionController.js';

const router = express.Router();

router.post('/bulk', bulkCreateSuggestions);
router.post('/', createSuggestion);
router.get('/', getSuggestions);
router.patch('/:id/status', updateStatus);

export default router;
