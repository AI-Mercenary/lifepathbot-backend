"""
Lemmatizer
Handles lemmatization using NLTK WordNet
"""
import nltk
from typing import List, Dict, Any
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet


class Lemmatizer:
    """Lemmatizes tokens to their base forms"""
    
    def __init__(self):
        # Download required NLTK data
        self._download_nltk_data()
        self.lemmatizer = WordNetLemmatizer()
    
    def _download_nltk_data(self):
        """Download required NLTK datasets"""
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet', quiet=True)
        
        try:
            nltk.data.find('corpora/omw-1.4')
        except LookupError:
            nltk.download('omw-1.4', quiet=True)
    
    def lemmatize_token(self, token: str, pos: str = 'n') -> str:
        """
        Lemmatize a single token
        
        Args:
            token: Word token
            pos: Part of speech ('n' for noun, 'v' for verb, 'a' for adjective, 'r' for adverb)
            
        Returns:
            Lemmatized token
        """
        return self.lemmatizer.lemmatize(token.lower(), pos=pos)
    
    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """
        Lemmatize a list of tokens (assumes nouns by default)
        
        Args:
            tokens: List of word tokens
            
        Returns:
            List of lemmatized tokens
        """
        lemmatized = []
        
        for token in tokens:
            # Try as noun first, then verb
            lemma_noun = self.lemmatizer.lemmatize(token.lower(), pos='n')
            lemma_verb = self.lemmatizer.lemmatize(token.lower(), pos='v')
            
            # Use the shorter form (more reduced)
            lemma = lemma_verb if len(lemma_verb) < len(lemma_noun) else lemma_noun
            lemmatized.append(lemma)
        
        return lemmatized
    
    def process_paragraph(self, paragraph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process paragraph and add lemmatized tokens
        
        Args:
            paragraph: Paragraph dictionary with tokens
            
        Returns:
            Enhanced paragraph with lemmatized tokens
        """
        if "tokens" in paragraph:
            paragraph["lemmatized_tokens"] = self.lemmatize_tokens(paragraph["tokens"])
        
        return paragraph
