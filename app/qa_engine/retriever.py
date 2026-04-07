"""
Retriever
Retrieves candidate paragraphs using inverted index
"""
from typing import List, Dict, Any, Set


class Retriever:
    """Retrieves candidate paragraphs for a query"""
    
    def __init__(self, inverted_index, knowledge_store):
        self.inverted_index = inverted_index
        self.knowledge_store = knowledge_store
    
    def retrieve(self, query: Dict[str, Any], max_candidates: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieve candidate paragraphs for query
        
        Args:
            query: Processed query dictionary
            max_candidates: Maximum number of candidates to return
            
        Returns:
            List of candidate paragraph dictionaries
        """
        # Get search terms
        search_terms = query["lemmatized_tokens"]
        key_phrases = query.get("key_phrases", [])
        
        # Strategy 1: Search with all terms
        para_ids = self.inverted_index.search(search_terms)
        
        # Strategy 2: Also search for key phrases
        for phrase in key_phrases:
            phrase_normalized = phrase.lower().replace(" ", "_")
            phrase_para_ids = self.inverted_index.search([phrase_normalized])
            para_ids.update(phrase_para_ids)
        
        # Strategy 3: If no results, try each term individually (more lenient)
        if not para_ids and search_terms:
            for term in search_terms:
                term_para_ids = self.inverted_index.search([term])
                para_ids.update(term_para_ids)
        
        # Strategy 4: If still no results, try with key phrases directly (not just normalized)
        if not para_ids and key_phrases:
            for phrase in key_phrases:
                phrase_tokens = phrase.lower().split()
                phrase_para_ids = self.inverted_index.search(phrase_tokens)
                para_ids.update(phrase_para_ids)

        # Strategy 5: If still no results, try with original tokens (before lemmatization)
        if not para_ids:
            original_tokens = query.get("tokens", [])
            if original_tokens:
                para_ids = self.inverted_index.search(original_tokens)
        
        # Debug logging (console)
        print(f"DEBUG: Retriever found {len(para_ids)} candidates for terms {search_terms}")
        
        # Get paragraph objects
        paragraphs = self.knowledge_store.get_paragraphs_by_ids(list(para_ids))
        
        # Limit candidates
        return paragraphs[:max_candidates]
    
    def retrieve_by_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve paragraphs by specific keywords
        
        Args:
            keywords: List of keywords
            
        Returns:
            List of paragraph dictionaries
        """
        para_ids = self.inverted_index.search(keywords)
        return self.knowledge_store.get_paragraphs_by_ids(list(para_ids))
