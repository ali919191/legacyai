from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import uuid
from ..memory_capture_service import MemoryCaptureService


@dataclass
class InterviewQuestion:
    """Represents a structured interview question."""
    id: str
    category: str
    question_text: str
    follow_up_prompts: List[str]


@dataclass
class InterviewResponse:
    """Represents a user's response to an interview question."""
    id: str
    user_id: str
    question_id: str
    response_text: str
    timestamp: datetime
    metadata: Dict[str, Any]


class StructuredInterviewService:
    """
    Structured Interview Service for Legacy AI.

    This service guides users through systematic interviews designed to capture
    comprehensive life experiences, values, and wisdom. The structured approach
    ensures consistent data collection across different life domains, which significantly
    improves the quality of personality modeling and memory distillation.

    How this improves AI modeling:
    - Personality Modeling: Consistent questions across domains reveal patterns in
      communication style, values, decision-making, and emotional expression
    - Memory Distillation: Targeted questions about regrets, lessons, and advice
      provide rich material for extracting life wisdom and guiding principles
    - Data Quality: Structured format reduces gaps and ensures comprehensive coverage
      of important life experiences

    The service automatically converts interview responses into memory entries,
    enriching the knowledge base for future AI interactions.
    """

    def __init__(self, memory_service: MemoryCaptureService):
        """
        Initialize the Structured Interview Service.

        Args:
            memory_service: Instance of MemoryCaptureService for storing converted memories.
        """
        self.memory_service = memory_service
        self.responses: Dict[str, InterviewResponse] = {}
        self.questions = self._initialize_questions()

    def _initialize_questions(self) -> Dict[str, List[InterviewQuestion]]:
        """
        Initialize the question sets for each life domain.

        Returns:
            Dictionary mapping categories to lists of questions.
        """
        return {
            "childhood": [
                InterviewQuestion(
                    id="childhood_001",
                    category="childhood",
                    question_text="What was your favorite childhood memory and why did it stand out to you?",
                    follow_up_prompts=[
                        "Who was with you during this memory?",
                        "What emotions do you associate with this experience?",
                        "How has this memory influenced your life?"
                    ]
                ),
                InterviewQuestion(
                    id="childhood_002",
                    category="childhood",
                    question_text="Describe a challenging experience from your childhood and what you learned from it.",
                    follow_up_prompts=[
                        "How did you overcome this challenge?",
                        "What support did you receive from others?",
                        "How has this shaped your resilience?"
                    ]
                ),
                InterviewQuestion(
                    id="childhood_003",
                    category="childhood",
                    question_text="What were your dreams and aspirations as a child?",
                    follow_up_prompts=[
                        "Which of these dreams came true?",
                        "What obstacles stood in your way?",
                        "How have your aspirations evolved?"
                    ]
                )
            ],
            "education": [
                InterviewQuestion(
                    id="education_001",
                    category="education",
                    question_text="What was your most memorable educational experience and why?",
                    follow_up_prompts=[
                        "Who was your favorite teacher and why?",
                        "What subjects did you excel in and why?",
                        "How did this experience shape your learning approach?"
                    ]
                ),
                InterviewQuestion(
                    id="education_002",
                    category="education",
                    question_text="Describe a time when you struggled academically and how you overcame it.",
                    follow_up_prompts=[
                        "What strategies helped you succeed?",
                        "Who supported you during this time?",
                        "What did you learn about perseverance?"
                    ]
                ),
                InterviewQuestion(
                    id="education_003",
                    category="education",
                    question_text="What life skills did you learn outside of formal education?",
                    follow_up_prompts=[
                        "How have these skills been valuable in your life?",
                        "Where did you learn these skills?",
                        "What skills do you wish you had learned earlier?"
                    ]
                )
            ],
            "career": [
                InterviewQuestion(
                    id="career_001",
                    category="career",
                    question_text="What was your most fulfilling career achievement and why?",
                    follow_up_prompts=[
                        "What skills did you use to achieve this?",
                        "Who helped you along the way?",
                        "How did this success change your perspective?"
                    ]
                ),
                InterviewQuestion(
                    id="career_002",
                    category="career",
                    question_text="Describe a career setback and what you learned from it.",
                    follow_up_prompts=[
                        "How did you recover from this setback?",
                        "What new opportunities emerged?",
                        "How has this experience influenced your work ethic?"
                    ]
                ),
                InterviewQuestion(
                    id="career_003",
                    category="career",
                    question_text="What work are you most proud of and why?",
                    follow_up_prompts=[
                        "What impact did this work have on others?",
                        "What challenges did you overcome?",
                        "How does this work reflect your values?"
                    ]
                )
            ],
            "relationships": [
                InterviewQuestion(
                    id="relationships_001",
                    category="relationships",
                    question_text="Describe the most important relationship in your life and why it mattered.",
                    follow_up_prompts=[
                        "How did this relationship develop over time?",
                        "What qualities made this relationship special?",
                        "How has this relationship influenced your other relationships?"
                    ]
                ),
                InterviewQuestion(
                    id="relationships_002",
                    category="relationships",
                    question_text="What have you learned about love and friendship from your experiences?",
                    follow_up_prompts=[
                        "What lessons about trust have you learned?",
                        "How do you show love to others?",
                        "What role have relationships played in your personal growth?"
                    ]
                ),
                InterviewQuestion(
                    id="relationships_003",
                    category="relationships",
                    question_text="Describe a relationship that taught you something important about yourself.",
                    follow_up_prompts=[
                        "What did you learn about your own needs?",
                        "How did this relationship change you?",
                        "What boundaries have you established as a result?"
                    ]
                )
            ],
            "failures_and_regrets": [
                InterviewQuestion(
                    id="failures_001",
                    category="failures_and_regrets",
                    question_text="What is your biggest regret in life and what did you learn from it?",
                    follow_up_prompts=[
                        "If you could go back, what would you do differently?",
                        "How has this regret influenced your decisions since?",
                        "What wisdom have you gained from this experience?"
                    ]
                ),
                InterviewQuestion(
                    id="failures_002",
                    category="failures_and_regrets",
                    question_text="Describe a failure that ultimately led to something positive.",
                    follow_up_prompts=[
                        "What unexpected opportunities emerged?",
                        "How did this failure change your perspective?",
                        "What would you tell others facing similar failures?"
                    ]
                ),
                InterviewQuestion(
                    id="failures_003",
                    category="failures_and_regrets",
                    question_text="What mistakes do you wish you had avoided, and why?",
                    follow_up_prompts=[
                        "What red flags did you miss?",
                        "How have you grown from recognizing these mistakes?",
                        "What advice would you give to avoid similar mistakes?"
                    ]
                )
            ],
            "life_lessons": [
                InterviewQuestion(
                    id="lessons_001",
                    category="life_lessons",
                    question_text="What is the most important life lesson you've learned?",
                    follow_up_prompts=[
                        "How did you learn this lesson?",
                        "How has this lesson influenced your daily life?",
                        "What lesson would you want your children to learn?"
                    ]
                ),
                InterviewQuestion(
                    id="lessons_002",
                    category="life_lessons",
                    question_text="What principle guides most of your decisions?",
                    follow_up_prompts=[
                        "How did you develop this principle?",
                        "Can you give an example of applying this principle?",
                        "How has this principle served you?"
                    ]
                ),
                InterviewQuestion(
                    id="lessons_003",
                    category="life_lessons",
                    question_text="What wisdom would you share with your younger self?",
                    follow_up_prompts=[
                        "What would you tell yourself about relationships?",
                        "What would you say about career choices?",
                        "What life skills would you emphasize?"
                    ]
                )
            ],
            "advice_for_children": [
                InterviewQuestion(
                    id="advice_001",
                    category="advice_for_children",
                    question_text="What is the most important advice you would give to your children?",
                    follow_up_prompts=[
                        "Why is this advice important to you?",
                        "Can you share a personal story that illustrates this advice?",
                        "How have you tried to live by this advice?"
                    ]
                ),
                InterviewQuestion(
                    id="advice_002",
                    category="advice_for_children",
                    question_text="What values do you hope your children will carry forward?",
                    follow_up_prompts=[
                        "How have you modeled these values?",
                        "What stories from your life demonstrate these values?",
                        "Why are these values important to future generations?"
                    ]
                ),
                InterviewQuestion(
                    id="advice_003",
                    category="advice_for_children",
                    question_text="What life skills do you wish to pass on to your children?",
                    follow_up_prompts=[
                        "How have you taught these skills?",
                        "What real-life situations require these skills?",
                        "How have these skills helped you in life?"
                    ]
                )
            ],
            "personal_beliefs": [
                InterviewQuestion(
                    id="beliefs_001",
                    category="personal_beliefs",
                    question_text="What core beliefs have guided your life?",
                    follow_up_prompts=[
                        "How did you develop these beliefs?",
                        "Can you share a story that demonstrates one of these beliefs?",
                        "How have these beliefs influenced your choices?"
                    ]
                ),
                InterviewQuestion(
                    id="beliefs_002",
                    category="personal_beliefs",
                    question_text="What do you believe about human nature?",
                    follow_up_prompts=[
                        "What experiences shaped this belief?",
                        "How does this belief affect your relationships?",
                        "Has this belief changed over time?"
                    ]
                ),
                InterviewQuestion(
                    id="beliefs_003",
                    category="personal_beliefs",
                    question_text="What gives your life meaning and purpose?",
                    follow_up_prompts=[
                        "How do you cultivate this sense of purpose?",
                        "What activities make you feel most alive?",
                        "How do you want to be remembered?"
                    ]
                )
            ]
        }

    def get_interview_categories(self) -> List[str]:
        """
        Get the list of available interview categories.

        Returns:
            List of category names.
        """
        return list(self.questions.keys())

    def get_questions_for_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all questions for a specific category.

        Args:
            category: The category name (e.g., 'childhood', 'career').

        Returns:
            List of question dictionaries with id, question_text, and follow_up_prompts.
        """
        if category not in self.questions:
            return []

        return [
            {
                "id": question.id,
                "question_text": question.question_text,
                "follow_up_prompts": question.follow_up_prompts
            }
            for question in self.questions[category]
        ]

    def record_interview_response(
        self,
        user_id: str,
        question_id: str,
        response: str
    ) -> str:
        """
        Record a user's response to an interview question.

        This method stores the response and automatically converts it to a memory entry.

        Args:
            user_id: The ID of the user providing the response.
            question_id: The ID of the question being answered.
            response: The user's response text.

        Returns:
            The ID of the recorded response.
        """
        response_id = str(uuid.uuid4())

        # Find the question to get category and metadata
        question = None
        category = None
        for cat, questions in self.questions.items():
            for q in questions:
                if q.id == question_id:
                    question = q
                    category = cat
                    break
            if question:
                break

        interview_response = InterviewResponse(
            id=response_id,
            user_id=user_id,
            question_id=question_id,
            response_text=response,
            timestamp=datetime.now(),
            metadata={
                "source": "structured_interview",
                "category": category,
                "question_text": question.question_text if question else ""
            }
        )

        self.responses[response_id] = interview_response

        # Automatically convert to memory
        self.convert_response_to_memory(user_id, interview_response)

        return response_id

    def convert_response_to_memory(self, user_id: str, response: InterviewResponse) -> str:
        """
        Convert an interview response into a memory entry.

        This method analyzes the response and question context to create appropriate
        memory metadata, ensuring the memory is properly tagged for interview origin.

        Args:
            user_id: The ID of the user (for future multi-user support).
            response: The InterviewResponse to convert.

        Returns:
            The ID of the created memory.
        """
        # Extract potential people, locations, and emotions from the response
        # This is a simplified implementation - in production, this could use NLP
        people_involved = self._extract_people_from_response(response.response_text)
        location = self._extract_location_from_response(response.response_text)
        emotions = self._extract_emotions_from_response(response.response_text)

        # Create memory title based on question category
        category_titles = {
            "childhood": "Childhood Memory",
            "education": "Educational Experience",
            "career": "Career Memory",
            "relationships": "Relationship Experience",
            "failures_and_regrets": "Life Lesson from Experience",
            "life_lessons": "Important Life Lesson",
            "advice_for_children": "Advice for Future Generations",
            "personal_beliefs": "Core Personal Belief"
        }

        title = f"{category_titles.get(response.metadata['category'], 'Interview Response')}: {response.metadata['question_text'][:50]}..."

        # Create tags indicating interview origin and category
        tags = [
            "interview_response",
            f"category_{response.metadata['category']}",
            "structured_interview"
        ]

        # Add emotion tags
        tags.extend([f"emotion_{emotion}" for emotion in emotions])

        # Create the memory
        memory_id = self.memory_service.create_memory(
            title=title,
            description=response.response_text,
            timestamp=response.timestamp,
            people_involved=people_involved,
            location=location,
            emotions=emotions,
            tags=tags
        )

        return memory_id

    def _extract_people_from_response(self, response_text: str) -> List[str]:
        """
        Extract potential people names from response text.

        This is a simplified implementation. In production, this would use
        named entity recognition or a more sophisticated NLP approach.

        Args:
            response_text: The response text to analyze.

        Returns:
            List of potential people names.
        """
        # Simple keyword-based extraction for common relationship terms
        relationship_keywords = [
            "mother", "father", "mom", "dad", "parent", "parents",
            "brother", "sister", "sibling", "siblings",
            "son", "daughter", "child", "children",
            "husband", "wife", "spouse", "partner",
            "friend", "friends", "colleague", "teacher", "mentor"
        ]

        found_people = []
        response_lower = response_text.lower()

        for keyword in relationship_keywords:
            if keyword in response_lower:
                found_people.append(keyword.title())

        return list(set(found_people))  # Remove duplicates

    def _extract_location_from_response(self, response_text: str) -> str:
        """
        Extract potential location from response text.

        Args:
            response_text: The response text to analyze.

        Returns:
            A location string if found, empty string otherwise.
        """
        # Simple extraction - look for common location indicators
        location_indicators = [" in ", " at ", " from ", " to "]

        for indicator in location_indicators:
            if indicator in response_text.lower():
                # Extract text after the indicator (simplified)
                parts = response_text.lower().split(indicator)
                if len(parts) > 1:
                    location_part = parts[1].split()[0]  # Take first word
                    if len(location_part) > 2:  # Avoid short words
                        return location_part.title()

        return ""

    def _extract_emotions_from_response(self, response_text: str) -> List[str]:
        """
        Extract potential emotions from response text.

        Args:
            response_text: The response text to analyze.

        Returns:
            List of emotion keywords found in the text.
        """
        emotion_keywords = [
            "happy", "sad", "joy", "anger", "fear", "love", "hate",
            "proud", "ashamed", "excited", "anxious", "grateful",
            "frustrated", "content", "regret", "hope", "disappointed",
            "fulfilled", "lonely", "loved", "respected", "cherished"
        ]

        found_emotions = []
        response_lower = response_text.lower()

        for emotion in emotion_keywords:
            if emotion in response_lower:
                found_emotions.append(emotion)

        return list(set(found_emotions))  # Remove duplicates