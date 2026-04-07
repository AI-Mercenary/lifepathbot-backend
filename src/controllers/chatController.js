import ChatMessage from '../models/ChatMessage.js';
import axios from 'axios';
import mongoose from 'mongoose';
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const pdf = require('pdf-parse');
const officeParser = require('officeparser');

// @desc    Save a chat message
// @route   POST /api/chat
// @access  Public
export const saveChatMessage = async (req, res) => {
  const { firebaseUid, userName, sessionId, role, text, agentType } = req.body;

  try {
    const message = await ChatMessage.create({
      firebaseUid,
      userName: userName || 'User',
      sessionId,
      role,
      text,
      agentType
    });
    res.status(201).json(message);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
};

// @desc    Get chat history for a specific user
// @route   GET /api/chat/:uid
// @access  Public
export const getUserChatHistory = async (req, res) => {
  const { uid } = req.params;
  try {
    const history = await ChatMessage.find({ firebaseUid: uid }).sort({ createdAt: 1 });
    res.json(history);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// @desc    Get ALL chat histories (for Admin)
// @route   GET /api/chat/admin/all
// @access  Admin
export const getAllChatHistoryForAdmin = async (req, res) => {
  try {
    const history = await ChatMessage.find({}).sort({ createdAt: -1 });
    res.json(history);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// @desc    Get unique chat sessions for a user
// @route   GET /api/chat/sessions/:uid
// @access  Public
export const getUserSessions = async (req, res) => {
  const { uid } = req.params;
  console.log("Fetching sessions for UID:", uid);
  try {
    const sessions = await ChatMessage.aggregate([
      { $match: { firebaseUid: uid } },
      { $sort: { createdAt: -1 } },
      { $group: {
          _id: "$sessionId",
          lastMessage: { $first: "$text" },
          agentType: { $first: "$agentType" },
          createdAt: { $first: "$createdAt" },
          messageCount: { $sum: 1 }
      }},
      { $sort: { createdAt: -1 } }
    ]);
    console.log(`Found ${sessions.length} sessions for user ${uid}`);
    res.json(sessions);
  } catch (error) {
    console.error("Aggregation Error:", error);
    res.status(500).json({ message: error.message });
  }
};

// @desc    Get messages for a specific session
// @route   GET /api/chat/session/:sessionId
// @access  Public
export const getSessionMessages = async (req, res) => {
    const { sessionId } = req.params;
    try {
        const messages = await ChatMessage.find({ sessionId }).sort({ createdAt: 1 });
        res.json(messages);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// @desc    Delete a specific session
// @route   DELETE /api/chat/session/:sessionId
// @access  Public
export const deleteChatSession = async (req, res) => {
    const { sessionId } = req.params;
    try {
        await ChatMessage.deleteMany({ sessionId });
        res.status(200).json({ success: true, message: 'Session deleted successfully' });
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
};

// @desc    Ask AI a message using RAG logic
// @route   POST /api/chat/ask
// @access  Public
export const askAI = async (req, res) => {
  const { message, context } = req.body;
  const agentType = context?.agentType || 'general';
  
  if (!message) {
      return res.status(400).json({ message: 'Message is required' });
  }

  try {
      const db = mongoose.connection.db;
      let prompt = "";

      if (agentType === 'study') {
          // 1. Fetch study material Context from mongo
          let pdfContext = "";
          try {
              const parsedCol = db.collection('parsed_pdfs');
              let doc = await parsedCol.findOne({}, { sort: { uploaded_at: -1 } });
              if(doc) {
                  if (doc.chunks && doc.chunks.length > 0) {
                      // Manual keyword overlap retrieval
                      const queryWords = message.toLowerCase().split(/\s+/).filter(w => w.length > 3);
                      let scoredChunks = doc.chunks.map(chunk => {
                          const lowerChunk = chunk.toLowerCase();
                          let score = 0;
                          queryWords.forEach(qw => {
                              if (lowerChunk.includes(qw)) score++;
                          });
                          return { chunk, score };
                      });
                      
                      // Sort by highest score first
                      scoredChunks.sort((a, b) => b.score - a.score);
                      // Take top 5 chunks for much better context
                      const topChunks = scoredChunks.slice(0, 5).map(c => c.chunk);
                      pdfContext = topChunks.join('\n...\n');
                  } else {
                      const content = doc.fullText || doc.paragraphs?.map(p => p.text).join('\n') || "";
                      pdfContext = content.substring(0, 4000); // Token limit
                  }
              }
          } catch (e) {
              console.error("PDF fetch error:", e);
          }

          if (!pdfContext) {
              return res.status(200).json({ response: "I don't see any uploaded study materials. Please upload a document first in Study Mode." });
          }

          prompt = `You are LifePathBot in Study Mode. Your strict instruction is to answer the User Question ONLY using the information provided in the Document Content below.
If the answer cannot be found in the Document Content, you MUST state that you do not have enough information to answer the question, and DO NOT provide any external knowledge.
Maintain a helpful and educational tone.

--- START DOCUMENT CONTENT ---
${pdfContext}
--- END DOCUMENT CONTENT ---

User Question: ${message}

Using ONLY the document content above, provide a detailed and accurate answer.`;
      } else {
          // General Mode - Use Suggestions and User Info
          let suggestionsContext = "";
          try {
              const suggestionsCol = db.collection('suggestions');
              const questionsCol = db.collection('questions');
              
              let suggestions = await suggestionsCol.find({status: 'approved'}).sort({createdAt: -1}).limit(30).toArray();
              let queries = await questionsCol.find({}).sort({createdAt: -1}).limit(15).toArray();

              let peerContext = [];
              if(suggestions && suggestions.length > 0) {
                  peerContext.push("Peer Suggestions:");
                  suggestions.forEach(s => peerContext.push(`- ${s.title}: ${s.description} (Category: ${s.category})`));
              }
              if(queries && queries.length > 0) {
                  peerContext.push("Recent Peer Discussions:");
                  queries.forEach(q => peerContext.push(`- Question: ${q.body} (Category: ${q.category})`));
              }
              suggestionsContext = peerContext.join('\n');
          } catch (e) {
              console.error("Context fetch error:", e);
          }

          prompt = `You are LifePathBot, an insightful and highly knowledgeable student companion.
You have been provided with "Peer Suggestions and Discussions" below from the community.
INSTRUCTION: Incorporate and emphasize the provided "Peer Suggestions and Discussions" into your answer if they are relevant to the user's question. 
If the provided context does not cover the user's topic (for example, if they ask about internships but the context has no internship advice), YOU MUST USE YOUR OWN extensive knowledge to provide excellent, accurate, and supportive guidance instead of saying there are no suggestions. Always be heavily supportive and actionable.

--- PEER SUGGESTIONS AND DISCUSSIONS ---
${suggestionsContext || "No peer discussions available."}
----------------------------------------

User Info: ${context?.userProfile?.name ? context.userProfile.name : 'Student'}.
User Message: ${message}

Provide a supportive, helpful, and highly detailed response based on both community context and your own knowledge.`;
      }

      // Request Groq API instead of Local Ollama
      const response = await axios.post('https://api.groq.com/openai/v1/chat/completions', {
          model: 'llama-3.3-70b-versatile',
          messages: [
              { role: 'user', content: prompt }
          ],
          temperature: 0.2
      }, { 
          headers: {
              'Authorization': `Bearer ${process.env.GROQ_API_KEY}`,
              'Content-Type': 'application/json'
          },
          timeout: 180000 
      });

      const botResponse = response.data.choices[0].message.content;
      res.status(200).json({ response: botResponse });

  } catch (error) {
      console.error("Groq API Error:", error.response?.data || error.message);
      res.status(500).json({ message: "I'm having trouble thinking right now. Please try again later.", error: error.message });
  }
};

// @desc    Upload and parse study material
// @route   POST /api/chat/upload-material
// @access  Public
export const uploadMaterial = async (req, res) => {
    if (!req.file) {
        return res.status(400).json({ message: 'No file uploaded' });
    }

    try {
        const dataBuffer = req.file.buffer;
        let textContent = '';
        const mimeType = req.file.mimetype;
        const originalName = req.file.originalname.toLowerCase();

        if (mimeType === 'application/pdf' || originalName.endsWith('.pdf')) {
            const data = await pdf(dataBuffer);
            textContent = data.text;
        } else {
            // Use officeparser for docx, pptx, etc.
            textContent = await officeParser.parseOffice(dataBuffer, { toText: true });
        }

        const db = mongoose.connection.db;
        const parsedCol = db.collection('parsed_pdfs');

        // Manual Chunking Parser (approx 400 words / ~600 tokens per chunk)
        const chunkText = (text, chunkSize = 400) => {
            const words = text.split(/\s+/);
            const chunks = [];
            for (let i = 0; i < words.length; i += chunkSize) {
                chunks.push(words.slice(i, i + chunkSize).join(' '));
            }
            return chunks;
        };
        const documentChunks = chunkText(textContent);

        const documentData = {
            document_id: `doc_${Date.now()}`,
            title: req.file.originalname,
            total_pages: 1, // Optional, since officeparser doesn't return pages
            fullText: textContent,
            chunks: documentChunks,
            uploaded_at: new Date()
        };

        await parsedCol.insertOne(documentData);

        res.status(200).json({
            success: true,
            message: 'Material uploaded and parsed successfully',
            data: {
                title: documentData.title,
                pages: documentData.total_pages
            }
        });
    } catch (error) {
        console.error("Parsing Error:", error);
        res.status(500).json({ message: 'Error parsing document', error: error.message });
    }
};
