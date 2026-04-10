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

from app.chatbot_engine import AcademicChatbot

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
                    # Save uploaded file temporarily
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    try:
                        result = st.session_state.chatbot.process_document(temp_path, uploaded_file.name)
                        
                        if result["success"]:
                            st.success(f"✅ Processed & Saved: {result['title']}")
                            st.info(f"📄 Pages: {result['pages']}")
                            st.info(f"📝 Paragraphs: {result['paragraphs']}")
                        else:
                            st.error(f"❌ Error: {result['error']}")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
        
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

