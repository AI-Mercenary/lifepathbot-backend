"""
Inverted Index
Creates and manages inverted index for fast keyword lookup
"""
from typing import List, Dict, Any, Set
from collections import defaultdict


class InvertedIndex:
    """Manages inverted index for paragraph retrieval"""
    
    def __init__(self):
        self.index = defaultdict(set)  # term -> set of para_ids
        self.ngram_index = defaultdict(set)  # n-gram -> set of para_ids
    
    def build_index(self, paragraphs: List[Dict[str, Any]]):
        """
        Build inverted index from paragraphs
        """
        for para in paragraphs:
            para_id = para["para_id"]
            
            # Index lemmatized tokens (normalized to lowercase)
            tokens = para.get("lemmatized_tokens", para.get("tokens", []))
            for token in tokens:
                self.index[token.lower()].add(para_id)
            
            # Index keywords
            keywords = para.get("keywords", [])
            for keyword in keywords:
                self.index[keyword.lower()].add(para_id)
            
            # Index bigrams
            bigrams = para.get("bigrams", [])
            for bigram in bigrams:
                self.ngram_index[bigram.lower()].add(para_id)
            
            # Index trigrams
            trigrams = para.get("trigrams", [])
            for trigram in trigrams:
                self.ngram_index[trigram.lower()].add(para_id)
    
    def search(self, terms: List[str]) -> Set[str]:
        """
        Search for paragraphs containing any of the terms (case-insensitive)
        """
        result_para_ids = set()
        
        for term in terms:
            term_lower = term.lower()
            # Search in main index
            if term_lower in self.index:
                result_para_ids.update(self.index[term_lower])
            
            # Search in n-gram index
            if term_lower in self.ngram_index:
                result_para_ids.update(self.ngram_index[term_lower])
        
        return result_para_ids
    
    def search_all(self, terms: List[str]) -> Set[str]:
        """
        Search for paragraphs containing ALL of the terms (AND operation, case-insensitive)
        """
        if not terms:
            return set()
        
        terms_lower = [t.lower() for t in terms]
        
        # Start with paragraphs containing first term
        result_para_ids = self.index.get(terms_lower[0], set()).copy()
        
        # Intersect with paragraphs containing other terms
        for term in terms_lower[1:]:
            term_para_ids = self.index.get(term, set())
            result_para_ids = result_para_ids.intersection(term_para_ids)
        
        return result_para_ids
    
    def get_term_frequency(self, term: str) -> int:
        """
        Get number of paragraphs containing term
        
        Args:
            term: Search term
            
        Returns:
            Number of paragraphs
        """
        return len(self.index.get(term, set()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert index to dictionary for serialization"""
        return {
            "index": {term: list(para_ids) for term, para_ids in self.index.items()},
            "ngram_index": {ngram: list(para_ids) for ngram, para_ids in self.ngram_index.items()}
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load index from dictionary"""
        self.index = defaultdict(set, {
            term: set(para_ids) for term, para_ids in data.get("index", {}).items()
        })
        self.ngram_index = defaultdict(set, {
            ngram: set(para_ids) for ngram, para_ids in data.get("ngram_index", {}).items()
        })
