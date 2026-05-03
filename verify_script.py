import asyncio
from dotenv import load_dotenv
load_dotenv()
from compare import SemanticComparator

async def test_comparison():
    comparator = SemanticComparator(method="gemini")
    
    teacher_data = {
        "pages": [
            {"content": "Q1. The capital of France is Paris.\nQ2. Photosynthesis is the process by which plants use sunlight to synthesize foods from carbon dioxide and water.", "page_no": 1}
        ]
    }
    
    student_data = {
        "pages": [
            {"content": "1. Paris is the capital of France.\n2. Plants make food using sunlight and carbon dioxide. This is called photosynthesis.", "page_no": 1}
        ]
    }
    
    print("Running comparison...")
    results = await comparator.compare_documents(teacher_data, student_data)
    
    import json
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(test_comparison())
