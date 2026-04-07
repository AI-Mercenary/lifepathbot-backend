"""
Test script to debug chatbot issues
"""
import sys
sys.path.insert(0, 'app')

from indexing.knowledge_store import KnowledgeStore
from indexing.inverted_index import InvertedIndex
from qa_engine.query_processor import QueryProcessor
from qa_engine.retriever import Retriever
from nlp_engine.tokenizer import Tokenizer
from nlp_engine.lemmatizer import Lemmatizer

# Load knowledge base
print("=" * 60)
print("LOADING KNOWLEDGE BASE")
print("=" * 60)

kb_store = KnowledgeStore()
kb = kb_store.load()

print(f"\n📊 Knowledge Base Stats:")
print(f"  - Total Documents: {len(kb.get('documents', []))}")
print(f"  - Total Paragraphs: {len(kb.get('paragraphs', []))}")

if kb.get('documents'):
    print(f"\n📄 Documents:")
    for doc in kb['documents']:
        print(f"  - {doc['title']} ({doc['total_pages']} pages, {doc['paragraph_count']} paragraphs)")

# Load inverted index
print(f"\n🔍 Inverted Index:")
inv_index = InvertedIndex()
if kb.get('inverted_index'):
    inv_index.from_dict(kb['inverted_index'])
    print(f"  - Total terms indexed: {len(inv_index.index)}")
    print(f"  - Total n-grams indexed: {len(inv_index.ngram_index)}")
    
    # Show sample terms
    sample_terms = list(inv_index.index.keys())[:10]
    print(f"\n  Sample terms: {', '.join(sample_terms)}")
else:
    print("  - No inverted index found!")

# Test a query
print("\n" + "=" * 60)
print("TESTING QUERY")
print("=" * 60)

test_question = "What is git init?"
print(f"\nQuestion: {test_question}")

# Initialize components
tokenizer = Tokenizer()
lemmatizer = Lemmatizer()
query_processor = QueryProcessor(tokenizer, lemmatizer)
retriever = Retriever(inv_index, kb_store)

# Process query
query = query_processor.process_query(test_question)
print(f"\n📝 Processed Query:")
print(f"  - Type: {query['type']}")
print(f"  - Tokens: {query['tokens']}")
print(f"  - Lemmatized: {query['lemmatized_tokens']}")

# Retrieve candidates
candidates = retriever.retrieve(query)
print(f"\n🔎 Retrieved Candidates: {len(candidates)}")

if candidates:
    print(f"\n📄 First candidate:")
    para = candidates[0]
    print(f"  - Para ID: {para['para_id']}")
    print(f"  - Page: {para.get('page', 'N/A')}")
    print(f"  - Text preview: {para['text'][:200]}...")
    print(f"  - Keywords: {para.get('keywords', [])[:5]}")
else:
    print("\n❌ No candidates found!")
    print("\nDEBUG: Trying to search for individual terms...")
    for term in query['lemmatized_tokens']:
        result = inv_index.search([term])
        print(f"  - '{term}': {len(result)} paragraphs")

print("\n" + "=" * 60)
