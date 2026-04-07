import sys
import os

# Add 'app' to python path
sys.path.insert(0, os.path.join(os.getcwd(), 'app'))

from answer_generator.ollama_generator import OllamaGenerator

def test_generation():
    print("Testing OllamaGenerator with model 'phi3.5'...")
    generator = OllamaGenerator(model_name="phi3.5")
    
    query = {"original_text": "What is the capital of France?"}
    contexts = [
        {"text": "Paris is the capital and most populous city of France.", "page": 1, "heading_text": "Geography"},
        {"text": "Lyon is a major city in France.", "page": 2, "heading_text": "Cities"}
    ]
    
    print("\nSending query...")
    try:
        result = generator.generate_answer(query, contexts)
        print("\n--- Result ---")
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Sources: {result['sources']}")
        
        if "Paris" in result['answer']:
            print("\n[SUCCESS] Verification Successful: Answer contains 'Paris'.")
        else:
            print("\n[WARNING] Verification Warning: Answer might not be correct.")
            
    except Exception as e:
        print(f"\n[ERROR] Verification Failed: {e}")

if __name__ == "__main__":
    test_generation()
