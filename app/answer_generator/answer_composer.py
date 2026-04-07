"""
Answer Composer
Composes final answers using templates
"""
from typing import List, Dict, Any


class AnswerComposer:
    """Composes answers from selected sentences"""
    
    def __init__(self):
        # Answer templates for different question types
        self.templates = {
            "definition": (
                "Based on the course materials:\n\n"
                "{answer_text}\n\n"
                "**Source:** {sources}"
            ),
            "procedure": (
                "Here's the process:\n\n"
                "{answer_text}\n\n"
                "**Reference:** {sources}"
            ),
            "explanation": (
                "According to the academic materials:\n\n"
                "{answer_text}\n\n"
                "**See:** {sources}"
            ),
            "comparison": (
                "Based on the course content:\n\n"
                "{answer_text}\n\n"
                "**Source:** {sources}"
            ),
            "example": (
                "From the course materials:\n\n"
                "{answer_text}\n\n"
                "**Reference:** {sources}"
            ),
            "general": (
                "{answer_text}\n\n"
                "**Found in:** {sources}"
            )
        }
    
    def compose_answer(self, sentences: List[Dict[str, Any]], 
                      query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compose final answer from selected sentences
        
        Args:
            sentences: List of selected sentence dictionaries
            query: Processed query
            
        Returns:
            Answer dictionary with text and metadata
        """
        if not sentences:
            return {
                "answer": "I couldn't find relevant information in the uploaded documents to answer this question.",
                "confidence": 0.0,
                "sources": []
            }
        
        # Get question type
        question_type = query.get("type", "general")
        
        # Order sentences logically
        ordered_sentences = self._order_sentences(sentences, question_type)
        
        # Compose answer text
        answer_text = self._format_sentences(ordered_sentences)
        
        # Format sources
        sources = self._format_sources(ordered_sentences)
        
        # Get template
        template = self.templates.get(question_type, self.templates["general"])
        
        # Fill template
        final_answer = template.format(
            answer_text=answer_text,
            sources=sources
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(sentences)
        
        return {
            "answer": final_answer,
            "confidence": confidence,
            "sources": self._get_source_list(ordered_sentences),
            "question_type": question_type
        }
    
    def _order_sentences(self, sentences: List[Dict[str, Any]], 
                        question_type: str) -> List[Dict[str, Any]]:
        """
        Order sentences logically based on question type
        
        Args:
            sentences: List of sentence dictionaries
            question_type: Type of question
            
        Returns:
            Ordered list of sentences
        """
        # For definition questions, prioritize first sentences
        if question_type == "definition":
            return sorted(sentences, key=lambda x: (not x["is_first"], -x["score"]))
        
        # For procedure questions, maintain document order
        elif question_type == "procedure":
            return sorted(sentences, key=lambda x: (x["page"], x["para_id"]))
        
        # For other types, use score
        else:
            return sorted(sentences, key=lambda x: -x["score"])
    
    def _format_sentences(self, sentences: List[Dict[str, Any]]) -> str:
        """
        Format sentences into readable text
        
        Args:
            sentences: List of sentence dictionaries
            
        Returns:
            Formatted text
        """
        # Join sentences with proper spacing
        formatted = []
        
        for sent in sentences:
            text = sent["text"].strip()
            
            # Ensure sentence ends with punctuation
            if not text[-1] in '.!?':
                text += '.'
            
            formatted.append(text)
        
        return " ".join(formatted)
    
    def _format_sources(self, sentences: List[Dict[str, Any]]) -> str:
        """
        Format source citations
        
        Args:
            sentences: List of sentence dictionaries
            
        Returns:
            Formatted source string
        """
        sources = []
        seen_pages = set()
        
        for sent in sentences:
            page = sent.get("page", 0)
            source_title = sent.get("source_title", "Document")
            
            if page not in seen_pages:
                if source_title:
                    sources.append(f"{source_title} (Page {page})")
                else:
                    sources.append(f"Page {page}")
                seen_pages.add(page)
        
        return ", ".join(sources) if sources else "Course materials"
    
    def _get_source_list(self, sentences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get structured source list
        
        Args:
            sentences: List of sentence dictionaries
            
        Returns:
            List of source dictionaries
        """
        sources = []
        seen_paras = set()
        
        for sent in sentences:
            para_id = sent.get("para_id")
            if para_id and para_id not in seen_paras:
                sources.append({
                    "para_id": para_id,
                    "page": sent.get("page", 0),
                    "title": sent.get("source_title", "")
                })
                seen_paras.add(para_id)
        
        return sources
    
    def _calculate_confidence(self, sentences: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence score for answer (0.00 - 1.00)
        
        1.00 = Exact match with all query terms
        0.90 = Very high match (most query terms found)
        0.70 = Good match (many query terms found)
        0.50 = Partial match (some query terms found)
        0.30 = Weak match (few query terms found)
        
        Args:
            sentences: List of sentence dictionaries with scores
            
        Returns:
            Confidence score between 0.00 and 1.00
        """
        if not sentences:
            return 0.0
        
        # Get the top sentence score (best match)
        top_score = sentences[0]["score"]
        
        # Calculate average score
        avg_score = sum(s["score"] for s in sentences) / len(sentences)
        
        # Normalize based on score ranges
        # Scores typically range from 0 to ~15 for good matches
        if top_score >= 10:
            # Excellent match - 0.90 to 1.00
            confidence = 0.90 + min((top_score - 10) / 50, 0.10)
        elif top_score >= 6:
            # Very good match - 0.70 to 0.90
            confidence = 0.70 + ((top_score - 6) / 4) * 0.20
        elif top_score >= 3:
            # Good match - 0.50 to 0.70
            confidence = 0.50 + ((top_score - 3) / 3) * 0.20
        elif top_score >= 1:
            # Partial match - 0.30 to 0.50
            confidence = 0.30 + ((top_score - 1) / 2) * 0.20
        else:
            # Weak match - 0.10 to 0.30
            confidence = 0.10 + (top_score * 0.20)
        
        # Adjust based on number of sentences (more sentences = higher confidence)
        sentence_bonus = min(len(sentences) * 0.05, 0.10)
        confidence = min(confidence + sentence_bonus, 1.0)
        
        # Ensure it's in valid range
        return round(max(0.0, min(confidence, 1.0)), 2)
