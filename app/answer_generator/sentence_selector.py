"""
Sentence Selector
Selects relevant sentences from paragraphs
"""
from typing import List, Dict, Any, Tuple
from nltk.tokenize import sent_tokenize


class SentenceSelector:
    """Selects relevant sentences for answer generation"""
    
    def __init__(self, tokenizer, lemmatizer):
        self.tokenizer = tokenizer
        self.lemmatizer = lemmatizer
    
    def select_sentences(self, ranked_paragraphs: List[Tuple[Dict[str, Any], float]], 
                        query: Dict[str, Any], max_sentences: int = 3) -> List[Dict[str, Any]]:
        """
        Select most relevant sentences from ranked paragraphs
        
        Args:
            ranked_paragraphs: List of (paragraph, score) tuples
            query: Processed query
            max_sentences: Maximum number of sentences to select
            
        Returns:
            List of sentence dictionaries with metadata
        """
        selected_sentences = []
        query_tokens = set(query["lemmatized_tokens"])
        
        for para, para_score in ranked_paragraphs:
            # Get sentences from paragraph
            sentences = para.get("cleaned_sentences", para.get("sentences", []))
            
            if not sentences:
                # Fallback: split text into sentences
                text = para.get("cleaned_text", para.get("text", ""))
                sentences = sent_tokenize(text)
            
            # Score each sentence
            for idx, sentence in enumerate(sentences):
                score = self._score_sentence(
                    sentence, 
                    query_tokens, 
                    idx, 
                    len(sentences),
                    para_score
                )
                
                selected_sentences.append({
                    "text": sentence,
                    "score": score,
                    "para_id": para["para_id"],
                    "page": para.get("page", 0),
                    "source_title": para.get("heading_text", ""),
                    "is_first": idx == 0
                })
        
        # Sort by score
        selected_sentences.sort(key=lambda x: x["score"], reverse=True)
        
        # Deduplicate similar sentences
        selected_sentences = self._deduplicate(selected_sentences)
        
        return selected_sentences[:max_sentences]
    
    def _score_sentence(self, sentence: str, query_tokens: set, 
                       position: int, total_sentences: int, para_score: float) -> float:
        """
        Score a sentence based on relevance
        
        Args:
            sentence: Sentence text
            query_tokens: Set of query tokens
            position: Position in paragraph (0-indexed)
            total_sentences: Total sentences in paragraph
            para_score: Paragraph's BM25 score
            
        Returns:
            Sentence score
        """
        # Tokenize and lemmatize sentence
        sent_tokens = self.tokenizer.process_text(sentence)
        sent_lemmas = set(self.lemmatizer.lemmatize_tokens(sent_tokens))
        
        # Calculate keyword overlap
        overlap = len(query_tokens.intersection(sent_lemmas))
        
        # Position bonus (first and last sentences often important)
        position_bonus = 1.0
        if position == 0:
            position_bonus = 1.5  # First sentence bonus
        elif position == total_sentences - 1:
            position_bonus = 1.1  # Last sentence bonus
        
        # Length penalty (very short or very long sentences)
        length_penalty = 1.0
        word_count = len(sent_tokens)
        if word_count < 5:
            length_penalty = 0.5
        elif word_count > 50:
            length_penalty = 0.8
        
        # Combine scores
        score = (overlap * position_bonus * length_penalty) + (para_score * 0.1)
        
        return score
    
    def _deduplicate(self, sentences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate or very similar sentences
        
        Args:
            sentences: List of sentence dictionaries
            
        Returns:
            Deduplicated list
        """
        unique_sentences = []
        seen_texts = set()
        
        for sent in sentences:
            # Normalize text for comparison
            normalized = sent["text"].lower().strip()
            
            # Check if we've seen this or very similar text
            if normalized not in seen_texts:
                unique_sentences.append(sent)
                seen_texts.add(normalized)
        
        return unique_sentences
