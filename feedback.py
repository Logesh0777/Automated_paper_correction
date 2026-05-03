"""
Feedback generation module that creates detailed, human-like feedback
explaining why marks were awarded or deducted.
"""
from typing import Dict, List, Any, Optional
import os
import httpx
from utils import get_api_key

class FeedbackGenerator:
    """Generates detailed feedback for student evaluations."""
    
    def __init__(self, use_ai: bool = False):
        """
        Initialize the feedback generator.
        
        Args:
            use_ai: Whether to use AI (OpenRouter) for generating feedback
        """
        self.use_ai = use_ai
        self.api_key = None
        
        if use_ai:
            try:
                self.api_key = os.getenv("OPENROUTER_API_KEY")
                if not self.api_key:
                    print("Warning: OPENROUTER_API_KEY not found in environment.")
                    self.use_ai = False
                self.model_name = "google/gemini-2.0-flash-001"
                self.api_url = "https://openrouter.ai/api/v1/chat/completions"
            except Exception as e:
                print(f"Warning: Could not initialize OpenRouter for feedback: {e}")
                self.use_ai = False
    
    def generate_item_feedback(
        self,
        item_score: Dict[str, Any],
        teacher_content: str = "",
        student_content: str = ""
    ) -> str:
        """
        Generate feedback for a single question.
        
        Args:
            item_score: Dictionary containing item scoring information
            teacher_content: Teacher's combined answer content (optional)
            student_content: Student's combined answer content (optional)
            
        Returns:
            Detailed feedback string
        """
        similarity = item_score['similarity_score']
        marks_awarded = item_score['marks_awarded']
        max_marks = item_score['max_marks']
        item_no = item_score['item_no']
        is_cheating = item_score.get('is_cheating_attempt', False)
        
        if is_cheating:
            return f"**Question {item_no} Feedback:**\n\n🚨 **YOU ARE CHEATING!** 🚨\n\nA Prompt Injection or grading manipulation attempt was detected in your answer block. You have been awarded **0 marks** for this question, and your normal feedback has been voided."
        
        if self.use_ai and self.api_key and teacher_content and student_content:
            return self._generate_ai_feedback(
                item_no, similarity, marks_awarded, max_marks,
                teacher_content, student_content
            )
        else:
            return self._generate_template_feedback(
                item_no, similarity, marks_awarded, max_marks
            )
    
    def _generate_template_feedback(
        self,
        item_no: Any,
        similarity: float,
        marks_awarded: float,
        max_marks: float
    ) -> str:
        """
        Generate template-based feedback.
        
        Args:
            item_no: Question number
            similarity: Similarity percentage
            marks_awarded: Marks awarded
            max_marks: Maximum possible marks
            
        Returns:
            Feedback string
        """
        feedback = f"**Question {item_no} Feedback:**\n\n"
        
        if similarity >= 90:
            feedback += "✅ **Excellent work!** Your answer demonstrates exceptional understanding. "
            feedback += "The content closely matches the expected answer with comprehensive coverage of key concepts. "
            feedback += f"You earned {marks_awarded}/{max_marks} marks.\n\n"
            feedback += "**Strengths:** Strong grasp of concepts, detailed explanations, accurate information."
        
        elif similarity >= 80:
            feedback += "✅ **Very good!** Your answer shows strong understanding with minor areas for improvement. "
            feedback += f"You earned {marks_awarded}/{max_marks} marks.\n\n"
            feedback += "**Strengths:** Good conceptual understanding, mostly accurate content.\n"
            feedback += "**Suggestions:** Consider adding more specific details or examples."
        
        elif similarity >= 70:
            feedback += "👍 **Good attempt.** Your answer captures most key points but could benefit from additional detail. "
            feedback += f"You earned {marks_awarded}/{max_marks} marks.\n\n"
            feedback += "**Strengths:** Basic concepts are understood.\n"
            feedback += "**Areas for improvement:** Provide more thorough explanations and include missing key points."
        
        elif similarity >= 60:
            feedback += "⚠️ **Satisfactory.** Your answer addresses the question but lacks depth or misses some important elements. "
            feedback += f"You earned {marks_awarded}/{max_marks} marks.\n\n"
            feedback += "**Strengths:** Some relevant points identified.\n"
            feedback += "**Areas for improvement:** Expand on core concepts, ensure accuracy, and cover all aspects of the question."
        
        elif similarity >= 50:
            feedback += "⚠️ **Needs improvement.** Your answer shows partial understanding but significant gaps remain. "
            feedback += f"You earned {marks_awarded}/{max_marks} marks.\n\n"
            feedback += "**Areas for improvement:** Review core concepts, provide more detailed explanations, "
            feedback += "and ensure your answer directly addresses the question."
        
        elif similarity >= 40:
            feedback += "❌ **Below expectations.** Your answer demonstrates limited understanding of the topic. "
            feedback += f"You earned {marks_awarded}/{max_marks} marks.\n\n"
            feedback += "**Recommendations:** Revisit the study material, focus on understanding fundamental concepts, "
            feedback += "and practice writing more structured answers."
        
        else:
            feedback += "❌ **Significant gaps.** Your answer shows minimal alignment with the expected response. "
            feedback += f"You earned {marks_awarded}/{max_marks} marks.\n\n"
            feedback += "**Recommendations:** Review the course material thoroughly, seek help to understand core concepts, "
            feedback += "and ensure you understand what the question is asking."
        
        return feedback
    
    def _generate_ai_feedback(
        self,
        item_no: Any,
        similarity: float,
        marks_awarded: float,
        max_marks: float,
        teacher_content: str,
        student_content: str
    ) -> str:
        """
        Generate AI-powered detailed feedback.
        
        Args:
            item_no: Question number
            similarity: Similarity percentage
            marks_awarded: Marks awarded
            max_marks: Maximum possible marks
            teacher_content: Teacher's answer
            student_content: Student's answer
            
        Returns:
            AI-generated feedback string
        """
        prompt = f"""
        As an educational evaluator, provide constructive feedback for a student's answer to Question {item_no}.
        
        Expected Answer Script (Teacher's Key):
        {teacher_content[:2000]}  # Limit to avoid token issues
        
        Student's Answer Script:
        {student_content[:2000]}
        
        Evaluation Details:
        - Question: {item_no}
        - Semantic Similarity: {similarity}%
        - Marks Awarded: {marks_awarded}/{max_marks}
        
        Please provide:
        1. What the student did well
        2. What was missing or incorrect
        3. Specific suggestions for improvement
        4. Overall assessment
        
        Keep the feedback encouraging, specific to Question {item_no}, and constructive. Limit to 150 words.
        """
        
        import time
        import re
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                time.sleep(2)  # Initial rate limiting delay
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://paper-corrector.app",
                    "X-Title": "Paper Corrector"
                }

                payload = {
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000
                }

                # Using httpx synchronous client as feedback is called iteratively inside synchronous pipeline
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(self.api_url, headers=headers, json=payload)
                    
                    if response.status_code != 200:
                        error_text = response.text
                        if response.status_code == 429:
                            raise Exception(f"429 Quota Exceeded: {error_text}")
                        else:
                            raise Exception(f"API Error {response.status_code}: {error_text}")
                            
                    result_json = response.json()
                    response_text = result_json["choices"][0]["message"]["content"]
                    
                return f"**Question {item_no} Feedback:**\n\n{response_text}"
                
            except Exception as e:
                error_str = str(e).lower()
                is_rate = "429" in error_str or "quota" in error_str or "exhausted" in error_str
                
                if is_rate and attempt < max_retries - 1:
                    match = re.search(r"retry(?:\s+in)?\s+(\d+(?:\.\d+)?)s?", error_str, re.IGNORECASE)
                    wait_time = float(match.group(1)) + 5 if match else 15 * (attempt + 1)
                    print(f"⚠️ Rate limit hit during feedback generation. Waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue
                    
                print(f"Error generating AI feedback: {e}")
                return self._generate_template_feedback(item_no, similarity, marks_awarded, max_marks)
    
    def generate_overall_feedback(self, evaluation: Dict[str, Any]) -> str:
        """
        Generate overall feedback for the entire evaluation.
        
        Args:
            evaluation: Complete evaluation results
            
        Returns:
            Overall feedback string
        """
        percentage = evaluation.get('percentage', 0.0)
        grade = evaluation.get('grade', 'N/A')
        status = evaluation.get('status', 'unknown')
        avg_similarity = evaluation.get('average_similarity', 0.0)
        
        feedback = "\n" + "="*60 + "\n"
        feedback += "OVERALL FEEDBACK\n"
        feedback += "="*60 + "\n\n"
        
        if status == "CHEATING DETECTED":
            feedback += "🚨 **FAIL: CHEATING DETECTED** 🚨\n\n"
            feedback += "A prompt injection or grading manipulation attempt was detected in one or more of your answers. "
            feedback += "As a result, your entire paper has been invalidated and awarded 0 marks. "
            feedback += "Academic integrity is taken very seriously.\n\n"
        elif percentage >= 85:
            feedback += "🌟 **Outstanding Performance!** You have demonstrated excellent mastery of the material. "
            feedback += "Your answers are comprehensive, well-structured, and accurate. Keep up the excellent work!\n\n"
        
        elif percentage >= 70:
            feedback += "✅ **Good Performance!** You have a solid understanding of most concepts. "
            feedback += "With a bit more attention to detail and depth, you can achieve even better results.\n\n"
        
        elif percentage >= 55:
            feedback += "👍 **Satisfactory Performance.** You grasp the basics but need to work on depth and accuracy. "
            feedback += "Review areas where you lost marks and practice writing more comprehensive answers.\n\n"
        
        elif percentage >= 40:
            feedback += "⚠️ **Marginal Performance.** You're just meeting the minimum requirements. "
            feedback += "Significant improvement is needed. Focus on understanding core concepts more thoroughly.\n\n"
        
        else:
            feedback += "❌ **Needs Significant Improvement.** Your performance indicates gaps in understanding. "
            feedback += "Please seek additional help, review the material carefully, and practice regularly.\n\n"
        
        feedback += f"**Final Grade:** {grade}\n"
        feedback += f"**Status:** {status.upper()}\n"
        feedback += f"**Overall Score:** {evaluation['total_score']}/{evaluation['max_score']}\n"
        feedback += f"**Average Semantic Match:** {avg_similarity}%\n\n"
        
        # Consistency analysis
        scores = [item['similarity_score'] for item in evaluation.get('item_scores', [])]
        if len(scores) > 1:
            score_variance = max(scores) - min(scores)
            if score_variance > 30:
                feedback += "**Note:** Your performance varies significantly across questions. "
                feedback += "Try to maintain consistency in your answers.\n"
            elif score_variance < 10:
                feedback += "**Note:** Your performance is consistent across all questions. "
                feedback += "Good job maintaining quality throughout!\n"
        
        return feedback
    
    def generate_complete_feedback(
        self,
        evaluation: Dict[str, Any],
        teacher_data: Optional[Dict] = None,
        student_data: Optional[Dict] = None
    ) -> str:
        """
        Generate complete feedback report including page-wise and overall feedback.
        
        Args:
            evaluation: Evaluation results
            teacher_data: Teacher's extracted data (optional, for AI feedback)
            student_data: Student's extracted data (optional, for AI feedback)
            
        Returns:
            Complete feedback report
        """
        complete_feedback = "\n" + "="*60 + "\n"
        complete_feedback += "DETAILED FEEDBACK REPORT\n"
        complete_feedback += "="*60 + "\n\n"
        
        # Question-wise feedback
        teacher_text = "\n\n".join([p.get('content', '') for p in teacher_data.get('pages', [])]) if teacher_data else ""
        student_text = "\n\n".join([p.get('content', '') for p in student_data.get('pages', [])]) if student_data else ""

        for item_score in evaluation.get('item_scores', []):
            item_feedback = self.generate_item_feedback(
                item_score, teacher_text, student_text
            )
            complete_feedback += item_feedback + "\n\n" + "-"*60 + "\n\n"
        
        # Overall feedback
        complete_feedback += self.generate_overall_feedback(evaluation)
        
        return complete_feedback
