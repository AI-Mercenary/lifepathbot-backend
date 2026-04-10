import os
import json
import requests
import pymongo
from datetime import datetime
from document_processor.pdf_extractor import PDFExtractor

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:1b"

class AcademicChatbot:
    """Main chatbot engine using MongoDB and native Ollama SLM"""
    
    def __init__(self):
        # Initialize component
        self.pdf_extractor = PDFExtractor()
        
        # Connect to MongoDB
        try:
            self.mongo_client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
            self.mongo_client.server_info() # Check connection
            self.db = self.mongo_client['lifepathbot_db']
            self.collection = self.db['parsed_pdfs']
            self.db_connected = True
        except Exception as e:
            print(f"⚠️ Could not connect to local MongoDB. Error: {e}")
            self.db_connected = False
            
    def process_document(self, file_path, original_name) -> dict:
        """
        Process uploaded document: Extract JSON -> Save to Mongo
        """
        if not self.db_connected:
            return {"success": False, "error": "MongoDB is not connected."}
            
        try:
            # 1. Extract text from PDF into structured JSON
            document_data = self.pdf_extractor.extract_from_file(file_path)
            
            # 2. Save directly to MongoDB
            document_data['uploaded_at'] = datetime.now()
            document_data['original_filename'] = original_name
            
            self.collection.insert_one(document_data)
            
            return {
                "success": True,
                "document_id": document_data["document_id"],
                "title": document_data["title"],
                "pages": document_data["total_pages"],
                "paragraphs": len(document_data["paragraphs"])
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_document_context(self) -> str:
        """Retrieve the latest document JSON from MongoDB to use as context"""
        if not self.db_connected:
            return ""
            
        doc = self.collection.find_one(sort=[('uploaded_at', pymongo.DESCENDING)])
        if not doc:
            return ""
            
        if '_id' in doc:
            del doc['_id']
            
        return json.dumps(doc, default=str)

    def get_suggestions_context(self) -> str:
        """Retrieve student suggestions to blend into chatbot responses"""
        if not self.db_connected:
            return ""
        
        try:
            suggestions_col = self.db['suggestions']
            suggestions = list(suggestions_col.find({"status": "approved"}, {"_id": 0, "title": 1, "description": 1, "category": 1, "tags": 1}).limit(20))
            if not suggestions:
                return "No student suggestions available yet."
            return json.dumps(suggestions, default=str)
        except Exception as e:
            return ""

    def answer_question(self, question: str) -> dict:
        """
        Answer a user question by sending JSON + prompt to Ollama
        """
        json_context = self.get_document_context()
        
        if not json_context:
            return {
                "answer": "There are no documents uploaded in MongoDB yet. Please upload a PDF first.",
                "confidence": 0.0,
                "sources": []
            }
            
        if len(json_context) > 10000:
            json_context = json_context[:10000] + "... [JSON TRUNCATED]"
            
        suggestions_context = self.get_suggestions_context()
        if len(suggestions_context) > 5000:
            suggestions_context = suggestions_context[:5000] + "... [SUGGESTIONS TRUNCATED]"
            
        prompt = f"""You are a helpful academic and student guidance assistant.
You have two sources of information to answer the user's question:

1. Academic Document Content (Extracted from PDF):
--- START PDF DATA ---
{json_context}
--- END PDF DATA ---

2. Student Peer Suggestions (From Google Forms):
--- START SUGGESTIONS ---
{suggestions_context}
--- END SUGGESTIONS ---

User Question: {question}

Using ONLY the information provided above, answer the question accurately and concisely. Combine academic info with peer guidance where appropriate.
"""
        
        try:
            response = requests.post(OLLAMA_URL, json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            })
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "answer": result.get("response", "No answer generated."),
                "confidence": 0.9,
                "sources": [{"page": "JSON", "title": "MongoDB Parsed Data"}]
            }
            
        except requests.exceptions.ConnectionError:
            return {
                "answer": "Could not connect to Ollama. Make sure Ollama is installed and running (`ollama serve`).",
                "confidence": 0.0,
                "sources": []
            }
        except Exception as e:
            return {
                "answer": f"Error running SLM processing: {str(e)}",
                "confidence": 0.0,
                "sources": []
            }
