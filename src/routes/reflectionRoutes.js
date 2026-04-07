import express from 'express';
import { getReflections, createReflection } from '../controllers/reflectionController.js';

const router = express.Router();

router.get('/:uid', getReflections);
router.post('/', createReflection);

export default router;
