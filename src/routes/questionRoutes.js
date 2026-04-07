import express from 'express';
import { createQuestion, getQuestions, answerQuestion } from '../controllers/questionController.js';

const router = express.Router();

router.post('/', createQuestion);
router.get('/', getQuestions);
router.post('/:id/answer', answerQuestion);

export default router;
