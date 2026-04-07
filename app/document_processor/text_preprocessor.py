"""
Text Preprocessor
Handles text cleaning and sentence segmentation
"""
import re
from typing import List, Dict, Any


class TextPreprocessor:
    """Preprocesses text for NLP processing"""
    
    def __init__(self):
        pass
    
    def preprocess_paragraph(self, paragraph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess a paragraph dictionary
        
        Args:
            paragraph: Paragraph dictionary from PDF extractor
            
        Returns:
            Enhanced paragraph with cleaned text
        """
        # Clean text
        cleaned_text = self.clean_text(paragraph["text"])
        
        # Update paragraph
        paragraph["cleaned_text"] = cleaned_text
        paragraph["cleaned_sentences"] = self._clean_sentences(paragraph["sentences"])
        
        return paragraph
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and special characters
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\']', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def _clean_sentences(self, sentences: List[str]) -> List[str]:
        """Clean individual sentences"""
        return [self.clean_text(s) for s in sentences if s.strip()]
    
    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text"""
        return ' '.join(text.split())
    
    def remove_page_numbers(self, text: str) -> str:
        """Remove page numbers from text"""
        # Remove standalone numbers at start or end of text
        text = re.sub(r'^\d+\s*', '', text)
        text = re.sub(r'\s*\d+$', '', text)
        return text
