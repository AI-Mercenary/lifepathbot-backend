"""
Ranker
Ranks paragraphs using BM25 algorithm
"""
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi


class Ranker:
    """Ranks paragraphs using BM25"""
    
    def __init__(self):
        self.bm25 = None
        self.paragraphs = []
    
    def rank(self, query: Dict[str, Any], paragraphs: List[Dict[str, Any]], 
             top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Rank paragraphs using BM25
        
        Args:
            query: Processed query dictionary
            paragraphs: List of candidate paragraphs
            top_k: Number of top paragraphs to return
            
        Returns:
            List of (paragraph, score) tuples
        """
        if not paragraphs:
            return []
        
        # Prepare corpus (tokenized paragraphs)
        corpus = []
        for para in paragraphs:
            tokens = para.get("lemmatized_tokens", para.get("tokens", []))
            corpus.append(tokens)
        
        # Build BM25 index
        self.bm25 = BM25Okapi(corpus)
        self.paragraphs = paragraphs
        
        # Get query tokens
        query_tokens = query["lemmatized_tokens"]
        
        # Calculate BM25 scores
        scores = self.bm25.get_scores(query_tokens)
        
        # Combine paragraphs with scores
        ranked = list(zip(paragraphs, scores))
        
        # Sort by score (descending)
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        # Apply additional heuristics
        ranked = self._apply_heuristics(ranked, query)
        
        return ranked[:top_k]
    
    def _apply_heuristics(self, ranked: List[Tuple[Dict[str, Any], float]], 
                          query: Dict[str, Any]) -> List[Tuple[Dict[str, Any], float]]:
        """
        Apply additional ranking heuristics
        
        Args:
            ranked: List of (paragraph, score) tuples
            query: Processed query
            
        Returns:
            Re-ranked list
        """
        question_type = query.get("type", "general")
        
        # Boost paragraphs based on question type
        boosted = []
        for para, score in ranked:
            boost = 1.0
            
            # Boost headings for definition questions
            if question_type == "definition" and para.get("heading"):
                boost = 1.5
            
            # Boost paragraphs with question marks for explanation questions
            if question_type == "explanation" and "?" in para.get("text", ""):
                boost = 1.2
            
            # Boost first paragraphs (often contain introductions/definitions)
            if para.get("page", 0) == 1:
                boost *= 1.1
            
            boosted.append((para, score * boost))
        
        # Re-sort
        boosted.sort(key=lambda x: x[1], reverse=True)
        
        return boosted
