import asyncio
import os
from pipeline import run_correction_pipeline
from compare import compare_documents_sync
from evaluation import Evaluator

def test_compare_logic():
    print("Testing dynamic marking logic...")
    
    # Mock data
    teacher_data = {
        "pages": [
            {"content": "Q1. What is the capital of France? A: Paris. (Weight: low)\nQ2. Explain the process of photosynthesis in detail. A: It is the process by which green plants and some other organisms use sunlight to synthesize foods from carbon dioxide and water. Photosynthesis in plants generally involves the green pigment chlorophyll and generates oxygen as a byproduct. (Weight: high)"}
        ]
    }
    
    student_data = {
        "pages": [
            {"content": "1. Paris is the capital. 2. Photosynthesis is how plants make food using sunlight and water."}
        ]
    }
    
    # Needs GEMINI_API_KEY environment variable. If not set, it'll fallback (which we updated to return total_marks).
    print("Calling compare_documents_sync...")
    results = compare_documents_sync(teacher_data, student_data, method="gemini", total_marks=100.0)
    
    print("\n--- LLM Results ---")
    for r in results:
        print(r)
        
    print("\n--- Evaluator Logic ---")
    evaluator = Evaluator(total_marks=100.0)
    evaluation = evaluator.evaluate_comparisons(results)
    
    for item in evaluation['item_scores']:
        print(f"Q{item['item_no']}: {item['marks_awarded']} / {item['max_marks']} (Similarity: {item['similarity_score']}%)")
        
    print(f"\nTotal Max Marks derived: {sum(item['max_marks'] for item in evaluation['item_scores'])}")

if __name__ == '__main__':
    from utils import get_api_key
    import google.generativeai as genai
    api_key = get_api_key("GEMINI_API_KEY")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        
    test_compare_logic()
