"""
Query Processor
Processes user questions for retrieval
"""
from typing import Dict, Any, List
import re


class QueryProcessor:
    """Processes user queries"""
    
    def __init__(self, tokenizer, lemmatizer):
        self.tokenizer = tokenizer
        self.lemmatizer = lemmatizer
        
        # Question type patterns
        self.question_patterns = {
            "definition": [
                r"^what is",
                r"^what are",
                r"^define",
                r"^what does .* mean",
                r"^meaning of"
            ],
            "procedure": [
                r"^how to",
                r"^how do",
                r"^how can",
                r"^steps to",
                r"^process of"
            ],
            "explanation": [
                r"^why",
                r"^explain",
                r"^describe",
                r"^what causes",
                r"^reason for"
            ],
            "comparison": [
                r"^difference between",
                r"^compare",
                r"^versus",
                r"vs\.",
                r"^what.*different"
            ],
            "example": [
                r"^give.*example",
                r"^show.*example",
                r"^what.*example"
            ]
        }
    
    def process_query(self, question: str) -> Dict[str, Any]:
        """
        Process user question
        
        Args:
            question: User's question
            
        Returns:
            Processed query dictionary
        """
        # Classify question type
        question_type = self.classify_question(question)
        
        # Extract keywords
        tokens = self.tokenizer.process_text(question)
        lemmatized = self.lemmatizer.lemmatize_tokens(tokens)
        
        # Extract key phrases (for multi-word concepts)
        key_phrases = self.extract_key_phrases(question)
        
        return {
            "original": question,
            "type": question_type,
            "tokens": tokens,
            "lemmatized_tokens": lemmatized,
            "key_phrases": key_phrases
        }
    
    def classify_question(self, question: str) -> str:
        """
        Classify question type
        
        Args:
            question: User's question
            
        Returns:
            Question type (definition, procedure, explanation, etc.)
        """
        question_lower = question.lower().strip()
        
        for q_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return q_type
        
        return "general"
    
    def extract_key_phrases(self, question: str) -> List[str]:
        """
        Extract key phrases from question (quoted terms, capitalized terms)
        
        Args:
            question: User's question
            
        Returns:
            List of key phrases
        """
        phrases = []
        
        # Extract quoted phrases
        quoted = re.findall(r'"([^"]+)"', question)
        phrases.extend(quoted)
        
        # Extract capitalized multi-word terms (likely proper nouns/concepts)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', question)
        phrases.extend(capitalized)
        
        return phrases
