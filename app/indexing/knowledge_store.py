"""
Knowledge Store
Manages JSON-based knowledge storage
"""
import json
import os
from typing import Dict, Any, List
from datetime import datetime


class KnowledgeStore:
    """Manages knowledge base storage in JSON format"""
    
    def __init__(self, storage_path: str = "app/data/knowledge_base.json"):
        self.storage_path = storage_path
        self.knowledge_base = {
            "metadata": {},
            "documents": [],
            "paragraphs": [],
            "inverted_index": {}
        }
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
    
    def save_document(self, document_data: Dict[str, Any], inverted_index: Any = None):
        """
        Save document to knowledge base
        
        Args:
            document_data: Document dictionary from PDF extractor
            inverted_index: InvertedIndex object (optional)
        """
        # Update metadata
        self.knowledge_base["metadata"] = {
            "last_updated": datetime.now().isoformat(),
            "total_documents": len(self.knowledge_base["documents"]) + 1,
            "total_paragraphs": len(self.knowledge_base["paragraphs"]) + len(document_data["paragraphs"])
        }
        
        # Add document
        doc_metadata = {
            "document_id": document_data["document_id"],
            "title": document_data["title"],
            "source_path": document_data["source_path"],
            "total_pages": document_data["total_pages"],
            "paragraph_count": len(document_data["paragraphs"])
        }
        self.knowledge_base["documents"].append(doc_metadata)
        
        # Add paragraphs
        self.knowledge_base["paragraphs"].extend(document_data["paragraphs"])
        
        # Add inverted index
        if inverted_index:
            self.knowledge_base["inverted_index"] = inverted_index.to_dict()
        
        # Save to file
        self._save_to_file()
    
    def load(self) -> Dict[str, Any]:
        """
        Load knowledge base from file
        
        Returns:
            Knowledge base dictionary
        """
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
        
        return self.knowledge_base
    
    def _save_to_file(self):
        """Save knowledge base to JSON file"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
    
    def get_paragraph_by_id(self, para_id: str) -> Dict[str, Any]:
        """
        Get paragraph by ID
        
        Args:
            para_id: Paragraph ID
            
        Returns:
            Paragraph dictionary or None
        """
        for para in self.knowledge_base["paragraphs"]:
            if para["para_id"] == para_id:
                return para
        return None
    
    def get_paragraphs_by_ids(self, para_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple paragraphs by IDs
        
        Args:
            para_ids: List of paragraph IDs
            
        Returns:
            List of paragraph dictionaries
        """
        para_id_set = set(para_ids)
        return [
            para for para in self.knowledge_base["paragraphs"]
            if para["para_id"] in para_id_set
        ]
    
    def get_all_paragraphs(self) -> List[Dict[str, Any]]:
        """Get all paragraphs"""
        return self.knowledge_base["paragraphs"]
    
    def clear(self):
        """Clear knowledge base"""
        self.knowledge_base = {
            "metadata": {},
            "documents": [],
            "paragraphs": [],
            "inverted_index": {}
        }
        self._save_to_file()
