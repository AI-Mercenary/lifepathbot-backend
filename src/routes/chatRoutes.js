import express from 'express';
import multer from 'multer';
import { 
    saveChatMessage, 
    getUserChatHistory, 
    getAllChatHistoryForAdmin, 
    askAI, 
    getUserSessions, 
    getSessionMessages,
    uploadMaterial,
    deleteChatSession
} from '../controllers/chatController.js';

const router = express.Router();
const upload = multer({ storage: multer.memoryStorage() });

router.post('/ask', askAI);
router.post('/upload-material', upload.single('file'), uploadMaterial);
router.post('/', saveChatMessage);
router.get('/sessions/:uid', getUserSessions);
router.get('/session/:sessionId', getSessionMessages);
router.delete('/session/:sessionId', deleteChatSession);
router.get('/admin/all', getAllChatHistoryForAdmin);
router.get('/:uid', getUserChatHistory);

export default router;
