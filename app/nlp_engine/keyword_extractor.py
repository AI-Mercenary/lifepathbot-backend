"""
Keyword Extractor
Extracts keywords and n-grams using TF-IDF
"""
from typing import List, Dict, Any, Tuple
from collections import Counter
import math
from nltk import bigrams, trigrams


class KeywordExtractor:
    """Extracts keywords and n-grams from text"""
    
    def __init__(self):
        self.document_frequencies = {}  # Term -> number of documents containing it
        self.total_documents = 0
    
    def extract_ngrams(self, tokens: List[str], n: int = 2) -> List[Tuple[str, ...]]:
        """
        Extract n-grams from tokens
        
        Args:
            tokens: List of tokens
            n: N-gram size (2 for bigrams, 3 for trigrams)
            
        Returns:
            List of n-grams as tuples
        """
        if n == 2:
            return list(bigrams(tokens))
        elif n == 3:
            return list(trigrams(tokens))
        else:
            # General n-gram extraction
            return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
    
    def extract_bigrams(self, tokens: List[str]) -> List[str]:
        """Extract bigrams and join with underscore"""
        bg = self.extract_ngrams(tokens, n=2)
        return ['_'.join(gram) for gram in bg]
    
    def extract_trigrams(self, tokens: List[str]) -> List[str]:
        """Extract trigrams and join with underscore"""
        tg = self.extract_ngrams(tokens, n=3)
        return ['_'.join(gram) for gram in tg]
    
    def calculate_tf(self, tokens: List[str]) -> Dict[str, float]:
        """
        Calculate Term Frequency
        
        Args:
            tokens: List of tokens
            
        Returns:
            Dictionary of term -> TF score
        """
        if not tokens:
            return {}
        
        term_counts = Counter(tokens)
        total_terms = len(tokens)
        
        tf_scores = {
            term: count / total_terms 
            for term, count in term_counts.items()
        }
        
        return tf_scores
    
    def calculate_idf(self, term: str) -> float:
        """
        Calculate Inverse Document Frequency
        
        Args:
            term: Term to calculate IDF for
            
        Returns:
            IDF score
        """
        if self.total_documents == 0:
            return 0.0
        
        doc_freq = self.document_frequencies.get(term, 0)
        
        if doc_freq == 0:
            return 0.0
        
        return math.log(self.total_documents / doc_freq)
    
    def calculate_tfidf(self, tokens: List[str]) -> Dict[str, float]:
        """
        Calculate TF-IDF scores
        
        Args:
            tokens: List of tokens
            
        Returns:
            Dictionary of term -> TF-IDF score
        """
        tf_scores = self.calculate_tf(tokens)
        
        tfidf_scores = {
            term: tf * self.calculate_idf(term)
            for term, tf in tf_scores.items()
        }
        
        return tfidf_scores
    
    def update_document_frequencies(self, paragraphs: List[Dict[str, Any]]):
        """
        Update document frequencies for IDF calculation
        
        Args:
            paragraphs: List of paragraph dictionaries
        """
        self.total_documents = len(paragraphs)
        self.document_frequencies = {}
        
        for para in paragraphs:
            tokens = para.get("lemmatized_tokens", para.get("tokens", []))
            unique_tokens = set(tokens)
            
            for token in unique_tokens:
                self.document_frequencies[token] = self.document_frequencies.get(token, 0) + 1
    
    def extract_top_keywords(self, tokens: List[str], top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Extract top N keywords based on TF-IDF
        
        Args:
            tokens: List of tokens
            top_n: Number of top keywords to return
            
        Returns:
            List of (keyword, score) tuples
        """
        tfidf_scores = self.calculate_tfidf(tokens)
        
        # Sort by score
        sorted_keywords = sorted(
            tfidf_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return sorted_keywords[:top_n]
    
    def process_paragraph(self, paragraph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process paragraph and add keywords and n-grams
        
        Args:
            paragraph: Paragraph dictionary
            
        Returns:
            Enhanced paragraph with keywords
        """
        tokens = paragraph.get("lemmatized_tokens", paragraph.get("tokens", []))
        
        # Extract keywords
        keywords = self.extract_top_keywords(tokens, top_n=10)
        paragraph["keywords"] = [kw[0] for kw in keywords]
        paragraph["keyword_scores"] = dict(keywords)
        
        # Extract n-grams
        paragraph["bigrams"] = self.extract_bigrams(tokens)
        paragraph["trigrams"] = self.extract_trigrams(tokens)
        
        return paragraph
