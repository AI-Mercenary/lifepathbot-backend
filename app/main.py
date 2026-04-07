"""
Academic Chatbot - Main Streamlit Application
"""
import streamlit as st
import os
import json
import requests
import pymongo
from datetime import datetime

# Import PDF extractor
from document_processor.pdf_extractor import PDFExtractor

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:1b" # Extremely fast on i3 CPU

class AcademicChatbot:
    """Main chatbot application using MongoDB and native Ollama SLM"""
    
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
            st.warning(f"⚠️ Could not connect to local MongoDB. Please make sure MongoDB is running. Error: {e}")
            self.db_connected = False
            
    def process_document(self, pdf_file) -> dict:
        """
        Process uploaded PDF document: Extract JSON -> Save to Mongo
        """
        if not self.db_connected:
            return {"success": False, "error": "MongoDB is not connected."}
            
        # Save uploaded file temporarily
        temp_path = f"temp_{pdf_file.name}"
        with open(temp_path, "wb") as f:
            f.write(pdf_file.getbuffer())
        
        try:
            # 1. Extract text from PDF into structured JSON
            document_data = self.pdf_extractor.extract_from_file(temp_path)
            
            # Clean up empty/huge fields if needed to save space
            
            # 2. Save directly to MongoDB
            # Add timestamp for tracking
            document_data['uploaded_at'] = datetime.now()
            
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
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def get_document_context(self) -> str:
        """Retrieve the latest document JSON from MongoDB to use as context"""
        if not self.db_connected:
            return ""
            
        doc = self.collection.find_one(sort=[('uploaded_at', pymongo.DESCENDING)])
        if not doc:
            return ""
            
        # We drop _id so it's JSON serializable
        if '_id' in doc:
            del doc['_id']
            
        return json.dumps(doc, default=str)

    def get_suggestions_context(self) -> str:
        """Retrieve student suggestions to blend into chatbot responses"""
        if not self.db_connected:
            return ""
        
        try:
            suggestions_col = self.db['suggestions']
            # Fetch up to 20 approved suggestions to prevent context overflow on i3 CPU
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
        # 1. Retrieve the parsed JSON from MongoDB
        json_context = self.get_document_context()
        
        if not json_context:
            return {
                "answer": "There are no documents uploaded in MongoDB yet. Please upload a PDF first.",
                "confidence": 0.0,
                "sources": []
            }
            
        # Truncate JSON if it's too large to prevent i3 CPU crashing
        # 5000 characters is a safe limit for 1B/3B models on an i3
        if len(json_context) > 10000:
            json_context = json_context[:10000] + "... [JSON TRUNCATED]"
            
        suggestions_context = self.get_suggestions_context()
        if len(suggestions_context) > 5000:
            suggestions_context = suggestions_context[:5000] + "... [SUGGESTIONS TRUNCATED]"
            
        # 2. Build the System Prompt
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
        
        # 3. Request Ollama
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


def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="Academic Chatbot (SLM + Mongo)",
        page_icon="📚",
        layout="wide"
    )
    
    # Title
    st.title("📚 Academic Chatbot (Local SLM + MongoDB)")
    st.markdown(f"*Uses **MongoDB** for JSON storage and **{OLLAMA_MODEL}** via Ollama on i3 CPU.*")
    
    # Initialize chatbot in session state
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = AcademicChatbot()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar for document upload
    with st.sidebar:
        st.header("📄 Document Upload")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload PDF to MongoDB",
            type=["pdf"],
            help="Upload academic PDFs (textbooks, lecture notes, etc.)"
        )
        
        if uploaded_file:
            if st.button("Extract JSON & Save to Mongo", type="primary"):
                with st.spinner("Extracting and saving to MongoDB..."):
                    result = st.session_state.chatbot.process_document(uploaded_file)
                    
                    if result["success"]:
                        st.success(f"✅ Processed & Saved: {result['title']}")
                        st.info(f"📄 Pages: {result['pages']}")
                        st.info(f"📝 Paragraphs: {result['paragraphs']}")
                    else:
                        st.error(f"❌ Error: {result['error']}")
        
        st.divider()
        
        # Knowledge base info
        st.header("📊 MongoDB Storage")
        if st.session_state.chatbot.db_connected:
            count = st.session_state.chatbot.collection.count_documents({})
            st.metric("Documents in MongoDB", count)
            
            if st.button("Clear MongoDB Documents"):
                st.session_state.chatbot.collection.delete_many({})
                st.success("MongoDB cleared!")
                st.rerun()
        else:
            st.error("No MongoDB Connection!")
    
    # Main chat interface
    st.header("💬 Ask Questions (JSON -> model)")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about the uploaded JSON data..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get answer
        with st.chat_message("assistant"):
            with st.spinner("SLM is reading JSON and thinking... (May take a little bit on i3 CPU)"):
                answer_data = st.session_state.chatbot.answer_question(prompt)
                
                st.markdown(answer_data["answer"])
                
                if answer_data.get("sources"):
                    with st.expander("📎 Sources"):
                        for source in answer_data.get("sources", []):
                            st.write(f"- {source['title']}")
        
        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer_data["answer"]
        })

if __name__ == "__main__":
    main()

