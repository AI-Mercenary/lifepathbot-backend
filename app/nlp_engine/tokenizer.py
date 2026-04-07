"""
Tokenizer
Handles tokenization using NLTK
"""
import nltk
from typing import List, Dict, Any
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords


class Tokenizer:
    """Tokenizes text into words and sentences"""
    
    def __init__(self):
        # Download required NLTK data
        self._download_nltk_data()
        self.stop_words = set(stopwords.words('english'))
    
    def _download_nltk_data(self):
        """Download required NLTK datasets"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """
        Tokenize text into sentences
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        return sent_tokenize(text)
    
    def tokenize_words(self, text: str, lowercase: bool = True) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Input text
            lowercase: Whether to convert to lowercase
            
        Returns:
            List of word tokens
        """
        if lowercase:
            text = text.lower()
        
        tokens = word_tokenize(text)
        return tokens
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords from token list
        
        Args:
            tokens: List of word tokens
            
        Returns:
            Filtered tokens without stopwords
        """
        return [token for token in tokens if token.lower() not in self.stop_words]
    
    def filter_alphanumeric(self, tokens: List[str]) -> List[str]:
        """
        Keep only alphanumeric tokens
        
        Args:
            tokens: List of word tokens
            
        Returns:
            Filtered alphanumeric tokens
        """
        return [token for token in tokens if token.isalnum()]
    
    def process_text(self, text: str, remove_stops: bool = True, 
                     filter_alpha: bool = True) -> List[str]:
        """
        Complete tokenization pipeline
        
        Args:
            text: Input text
            remove_stops: Whether to remove stopwords
            filter_alpha: Whether to filter non-alphanumeric tokens
            
        Returns:
            Processed token list
        """
        # Tokenize
        tokens = self.tokenize_words(text, lowercase=True)
        
        # Filter alphanumeric
        if filter_alpha:
            tokens = self.filter_alphanumeric(tokens)
        
        # Remove stopwords
        if remove_stops:
            tokens = self.remove_stopwords(tokens)
        
        return tokens
    
    def process_paragraph(self, paragraph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process paragraph dictionary and add tokens
        
        Args:
            paragraph: Paragraph dictionary
            
        Returns:
            Enhanced paragraph with tokens
        """
        text = paragraph.get("cleaned_text", paragraph.get("text", ""))
        
        # Tokenize
        paragraph["tokens"] = self.process_text(text)
        paragraph["all_tokens"] = self.tokenize_words(text, lowercase=True)
        
        return paragraph
