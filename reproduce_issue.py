
import sys
import os
sys.path.insert(0, 'app')

from indexing.inverted_index import InvertedIndex
from qa_engine.query_processor import QueryProcessor
from qa_engine.retriever import Retriever
from nlp_engine.tokenizer import Tokenizer
from nlp_engine.lemmatizer import Lemmatizer
from nlp_engine.keyword_extractor import KeywordExtractor
from indexing.knowledge_store import KnowledgeStore

def reproduce():
    # 1. Setup components
    tokenizer = Tokenizer()
    lemmatizer = Lemmatizer()
    extractor = KeywordExtractor()
    inv_index = InvertedIndex()
    
    # 2. Mock a paragraph
    paragraph = {
        "para_id": "p1",
        "text": "1. Basic Git Commands (For managing repositories)\ngit pull: Fetches and merges changes from the remote repository.",
        "cleaned_text": "1. Basic Git Commands (For managing repositories) git pull: Fetches and merges changes from the remote repository.",
    }
    
    # Process paragraph
    tokenizer.process_paragraph(paragraph)
    lemmatizer.process_paragraph(paragraph)
    extractor.process_paragraph(paragraph)
    
    print(f"Processed tokens: {paragraph['tokens']}")
    print(f"Lemmatized tokens: {paragraph['lemmatized_tokens']}")
    print(f"Bigrams: {paragraph['bigrams']}")
    
    # Build index
    inv_index.build_index([paragraph])
    print(f"Index keys: {list(inv_index.index.keys())}")
    print(f"Ngram Index keys: {list(inv_index.ngram_index.keys())}")
    
    # 3. Mock KnowledgeStore
    class MockKS:
        def get_paragraphs_by_ids(self, ids):
            return [paragraph] if "p1" in ids else []
    
    ks = MockKS()
    retriever = Retriever(inv_index, ks)
    qp = QueryProcessor(tokenizer, lemmatizer)
    
    # 4. Test Query
    question = "Git Pull"
    print(f"\nTesting Query: {question}")
    query = qp.process_query(question)
    print(f"Query Processed: {query}")
    
    candidates = retriever.retrieve(query)
    print(f"Candidates found: {len(candidates)}")
    if candidates:
        print(f"First candidate text: {candidates[0]['text']}")
    else:
        print("FAILED: No candidates found!")

if __name__ == "__main__":
    reproduce()
