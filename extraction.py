"""
Text extraction module with sequential safe-mode processing.
Uses OpenRouter API with:
  - One page per API call for simplicity and reliability
  - Exponential backoff for transient 429 errors
"""
import asyncio
import os
import json
import time
import threading
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from PIL import Image
import io
import base64
import httpx
from pdf2image import convert_from_path




# Thread-safe semaphore (1 request at a time). Using threading.Semaphore avoids
# asyncio event-loop issues when called from Streamlit's thread context.
_rate_limit_lock = threading.Semaphore(1)


class DocumentExtractor:
    """Handles text extraction from PDF or Images using OpenRouter."""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables. Please check your .env file.")
            
        self.model_name = "google/gemini-2.0-flash-lite-001"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    # ── Single-page transcription (synchronous) ───────────────────────
    def _transcribe_page_sync(
        self, image: Image.Image, page_number: int, source_type: str = "exam paper"
    ) -> Dict[str, Any]:
        """
        Transcribe a single page. Synchronous and thread-safe.
        """
        with _rate_limit_lock:
            max_retries = 5
            initial_delay = 3

            for attempt in range(max_retries):
                try:
                    prompt = (
                        f"Transcribe the text from this {source_type} page exactly as written. "
                        "CRITICAL: The text may be in English, Tamil, or a mix of both. You MUST NOT translate Tamil text into English. "
                        "If a word is written in Tamil script, you MUST extract and output it in the original Tamil characters in the 'content' field. "
                        "Pay special attention to correctly identifying and transcribing Tamil handwriting. "
                        "Preserve all question numbers, parts, sub-parts, and logical structure. "
                        "IMPORTANT: If marks are printed next to any question (e.g., '[5 marks]', '(10)', 'Marks: 5'), "
                        "include them in the transcription AND list them separately in 'marks_allocation'. "
                        "Additionally, provide a 'confidence_score' between 0 and 100 "
                        "representing your confidence in reading the handwriting/text clearly. "
                        "You must strictly aim to have a confidence score above 96. "
                        "If you must output a confidence score below 96, you must explain exactly why "
                        "in 'confidence_reason' (e.g., 'smudged ink on Q3', 'camera glare'). "
                        "If the score is 96 or above, 'confidence_reason' can be empty or 'Clear text'.\n"
                        "Return the result STRICTLY as a JSON object with this shape:\n"
                        "{\n"
                        '  "content": "<transcribed text>",\n'
                        '  "confidence_score": 98,\n'
                        '  "confidence_reason": "Clear text",\n'
                        '  "marks_allocation": [{"question": "1a", "marks": 5}]\n'
                        "}\n"
                        "If no marks are visible, set marks_allocation to an empty array []."
                    )

                    # Convert image to base64
                    if image.mode != "RGB":
                        image = image.convert("RGB")
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG", quality=85)  # balanced quality for reliable OCR
                    base64_img = base64.b64encode(buffered.getvalue()).decode("utf-8")

                    content_list = [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ]

                    payload = {
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": content_list}],
                        "max_tokens": 4096,
                        "temperature": 0.0,
                        "top_p": 1.0
                    }

                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://paper-corrector.app",
                        "X-Title": "Paper Corrector"
                    }

                    time.sleep(initial_delay)

                    with httpx.Client(timeout=180.0) as client:
                        response = client.post(self.api_url, headers=headers, json=payload)

                        if response.status_code != 200:
                            error_text = response.text
                            if response.status_code == 429:
                                raise Exception(f"429 Quota Exceeded: {error_text}")
                            else:
                                raise Exception(f"API Error {response.status_code}: {error_text}")

                        result_json = response.json()
                        raw = result_json["choices"][0]["message"]["content"] or "{}"

                    try:
                        clean_text = raw.strip()
                        if clean_text.startswith("```"):
                            clean_text = re.sub(r'^```(?:json)?\s*', '', clean_text, flags=re.IGNORECASE)
                            clean_text = re.sub(r'\s*```$', '', clean_text.strip())
                        # Try to find a JSON object
                        start_idx = clean_text.find('{')
                        end_idx = clean_text.rfind('}')
                        if start_idx != -1 and end_idx != -1:
                            clean_text = clean_text[start_idx:end_idx+1]
                        data = json.loads(clean_text)
                    except Exception as e:
                        print(f"JSON Parse Error (page {page_number}): {e} | Raw: {raw[:80]}...")
                        data = {"content": raw, "confidence_score": 50, "confidence_reason": f"JSON Parsing Failed: {e}"}

                    return {
                        "page_no": page_number,
                        "content": data.get("content", ""),
                        "confidence_score": data.get("confidence_score", 0),
                        "confidence_reason": data.get("confidence_reason", "No reason provided"),
                        "marks_allocation": data.get("marks_allocation", [])
                    }

                except Exception as e:
                    error_str = str(e)
                    is_rate = "429" in error_str or "quota" in error_str.lower() or "exhausted" in error_str.lower()

                    if is_rate and attempt < max_retries - 1:
                        match = re.search(r"retry(?:\s+in)?\s+(\d+(?:\.\d+)?)s?", error_str, re.IGNORECASE)
                        suggested = float(match.group(1)) + 2 if match else 15 * (attempt + 1)
                        wait_time = min(max(suggested, initial_delay + 5 * attempt), 120)
                        print(f"⚠️ Rate limit hit on page {page_number}. Waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}...")
                        time.sleep(wait_time)
                        continue

                    print(f"❌ Error on page {page_number}: {error_str}")
                    return {"page_no": page_number, "content": "", "confidence_score": 0, "confidence_reason": error_str, "marks_allocation": []}

        return {"page_no": page_number, "content": "", "confidence_score": 0, "confidence_reason": "Lock timeout", "marks_allocation": []}

    async def _transcribe_page(
        self, image: Image.Image, page_number: int, source_type: str = "exam paper"
    ) -> Dict[str, Any]:
        """Async wrapper — offloads the sync work to a thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._transcribe_page_sync, image, page_number, source_type)

    # ── File extraction ──────────────────────────────────────────────
    async def extract_from_file(self, file_path: str, source: str) -> Dict[str, Any]:
        """Extract text from a PDF or image file, one page at a time."""

        print(f"📑 Extracting {source} from: {Path(file_path).name}")

        try:
            file_ext = Path(file_path).suffix.lower()
            images: List[Image.Image] = []

            if file_ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]:
                print(f"   > Detected image file format: {file_ext}")
                images = [Image.open(file_path)]
            elif file_ext == ".pdf":
                print(f"   > Detected PDF file, converting to images...")
                images = convert_from_path(file_path, dpi=150)  # 150 DPI is sufficient and avoids large payloads
            else:
                raise ValueError(f"Unsupported format: {file_ext}. Use PDF or Images.")

            total_pages = len(images)
            print(f"   > Total pages: {total_pages}  |  1 page per API call")

            pages_content: List[Dict[str, Any]] = []

            for page_idx, img in enumerate(images):
                page_num = page_idx + 1
                print(f"   > Processing {source} page {page_num}/{total_pages}...")
                result = await self._transcribe_page(img, page_num, source_type=source)
                pages_content.append(result)

            pages_content.sort(key=lambda x: x["page_no"])
            print(f"✅ Completed extraction for {source}: {len(pages_content)} pages")

            result = {
                "source": source,
                "total_pages": len(pages_content),
                "pages": pages_content,
                "file_name": Path(file_path).name,
            }

            return result

        except Exception as e:
            print(f"❌ Error extracting from {source}: {str(e)}")
            return {
                "source": source,
                "total_pages": 0,
                "pages": [],
                "file_name": Path(file_path).name,
                "error": str(e),
            }


# ── Public API ───────────────────────────────────────────────────────

async def extract_documents(
    teacher_path: str,
    student_path: str,
    reference_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Extract text from teacher, student, and optional reference documents SEQUENTIALLY."""
    extractor = DocumentExtractor()

    # Priority 1: Reference (Few-Shot Calibration basis)
    reference_data = None
    if reference_path:
        reference_data = await extractor.extract_from_file(reference_path, "Reference Paper")
        
    # Priority 2: Teacher Key
    teacher_data = await extractor.extract_from_file(teacher_path, "Teacher Answer Script")
    
    # Priority 3: Student Script
    student_data = await extractor.extract_from_file(student_path, "Student Answer Script")

    return {
        "teacher_key": teacher_data,
        "student_script": student_data,
        "reference_paper": reference_data,
        "extraction_status": "completed",
    }


def extract_documents_sync(
    teacher_file_path: str,
    student_file_path: str,
    reference_file_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Synchronous wrapper for extracting documents."""
    return asyncio.run(
        extract_documents(teacher_file_path, student_file_path, reference_file_path)
    )