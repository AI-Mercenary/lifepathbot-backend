"""
PDF Text Extractor
Extracts text from PDF files while preserving structure and metadata
"""
import pdfplumber
from typing import List, Dict, Any
import re


class PDFExtractor:
    """Extracts text from PDF files with metadata preservation"""
    
    def __init__(self):
        self.current_doc = None
    
    def extract_from_file(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing document metadata and extracted paragraphs
        """
        document_data = {
            "document_id": self._generate_doc_id(pdf_path),
            "title": self._extract_title(pdf_path),
            "source_path": pdf_path,
            "total_pages": 0,
            "paragraphs": []
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                document_data["total_pages"] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extract text from page
                    text = page.extract_text()
                    
                    if text:
                        # Process page text into paragraphs
                        paragraphs = self._extract_paragraphs(
                            text, 
                            page_num, 
                            document_data["document_id"]
                        )
                        document_data["paragraphs"].extend(paragraphs)
        
        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")
        
        return document_data
    
    def _generate_doc_id(self, pdf_path: str) -> str:
        """Generate unique document ID from filename"""
        import os
        from datetime import datetime
        
        filename = os.path.basename(pdf_path)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"doc_{filename.replace('.pdf', '')}_{timestamp}"
    
    def _extract_title(self, pdf_path: str) -> str:
        """Extract document title from filename or metadata"""
        import os
        filename = os.path.basename(pdf_path)
        # Remove extension and clean up
        title = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
        return title.title()
    
    def _extract_paragraphs(self, page_text: str, page_num: int, doc_id: str) -> List[Dict[str, Any]]:
        """
        Extract paragraphs from page text
        
        Args:
            page_text: Raw text from page
            page_num: Page number
            doc_id: Document ID
            
        Returns:
            List of paragraph dictionaries
        """
        paragraphs = []
        
        # Split text into paragraphs (separated by double newlines or significant whitespace)
        raw_paragraphs = re.split(r'\n\s*\n', page_text)
        
        para_counter = 0
        for raw_para in raw_paragraphs:
            # Clean up paragraph
            para_text = raw_para.strip()
            
            # Skip very short paragraphs (likely noise)
            if len(para_text) < 20:
                continue
            
            para_counter += 1
            para_id = f"{doc_id}_p{page_num}_{para_counter}"
            
            # Detect if this is a heading (heuristic: short, title case, no ending punctuation)
            is_heading = self._is_heading(para_text)
            
            paragraph = {
                "para_id": para_id,
                "text": para_text,
                "page": page_num,
                "heading": is_heading,
                "heading_text": para_text if is_heading else None,
                "sentences": self._split_sentences(para_text),
                "char_count": len(para_text)
            }
            
            paragraphs.append(paragraph)
        
        return paragraphs
    
    def _is_heading(self, text: str) -> bool:
        """Detect if text is likely a heading"""
        # Heuristics for heading detection
        if len(text) > 100:
            return False
        
        # Check if mostly title case
        words = text.split()
        if len(words) == 0:
            return False
        
        title_case_words = sum(1 for w in words if w and w[0].isupper())
        title_case_ratio = title_case_words / len(words)
        
        # No ending punctuation (except question mark)
        ends_with_period = text.rstrip().endswith('.')
        
        return title_case_ratio > 0.5 and not ends_with_period
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split paragraph into sentences (basic implementation)"""
        # Simple sentence splitting (will be enhanced by NLP tokenizer)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
