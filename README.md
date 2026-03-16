# Legacy AI Platform

Legacy AI is a platform designed to capture and preserve life experiences as structured memories, enabling family members to interact with an AI representation of their loved one after they pass away.

## Features

- **Life Experience Capture**: Tools and interfaces to record personal stories, memories, and experiences.
- **Structured Memory Storage**: Organize and store memories in a structured format for AI processing.
- **AI Interaction**: Allow family members to converse with an AI-powered persona based on the stored memories.
- **Secure Access**: Posthumous access controls for designated family members.

## System Pipeline

The Legacy AI platform follows a comprehensive data processing pipeline that transforms personal stories into meaningful AI interactions:

**Family Interaction API → Structured Interview → Memory Capture → Media Memory Service → Timeline Engine → Memory Embeddings → Vector Search → Conversation Engine → Personality Model → Memory Distillation → Legacy Access Control → Response Moderation → AI Response**

### Pipeline Components

1. **Family Interaction API**: REST endpoints allowing beneficiaries to ask questions, browse memories, and explore timelines
2. **Structured Interview**: Guided question sets across life domains capture comprehensive personal experiences
3. **Memory Capture**: Converts interview responses and stories into structured memory entries with metadata
4. **Media Memory Service**: Handles upload and management of multimedia memories (photos, audio, video) linked to memory entries
5. **Timeline Engine**: Organizes memories chronologically and by life stages for contextual understanding
6. **Memory Embeddings**: Transforms memory text into vector representations for semantic search
7. **Vector Search**: Finds semantically similar memories using cosine similarity and embedding matching
7. **Conversation Engine**: Orchestrates memory retrieval, context building, and response generation
7. **Personality Model**: Analyzes memory patterns to create authentic personality profiles for personalized responses
8. **Memory Distillation**: Extracts higher-level wisdom, life lessons, and guidance from raw memories
9. **Legacy Access Control**: Implements privacy and access controls for authorized beneficiaries
10. **Response Moderation**: Ensures all AI responses remain appropriate, respectful, and safe for family interactions
11. **AI Response**: Delivers personalized, contextually appropriate answers to user questions

### Data Flow Integration

- **Interview responses** automatically become **structured memories** with rich metadata
- **Timeline context** enhances memory relevance by considering chronological relationships
- **Semantic embeddings** enable natural language queries to find relevant experiences
- **Vector search** provides fast, accurate memory retrieval for conversational context
- **Memory distillation** transforms raw memories into actionable wisdom and life lessons
- **Conversation engine** synthesizes multiple memory sources into coherent, personalized responses
- **Legacy access control** ensures privacy protection and authorized beneficiary access
- **Response moderation** filters and adjusts AI responses for safety and appropriateness

## Conversation Engine

The Conversation Engine is the core component that enables family members to interact with an AI representation of their loved one. It processes natural language queries and generates responses based on stored memories.

### Key Features

- **Semantic Memory Search**: Uses vector embeddings to find memories most relevant to user questions
- **Chronological Context**: Integrates timeline information to provide temporal context in responses
- **Distilled Wisdom Integration**: Incorporates life lessons, advice, and insights extracted from memories
- **Personality-Aware Responses**: Uses personality profiles for authentic, personalized interactions
- **Structured Response Format**: Returns responses with generated answers, memory references, insights used, and confidence scores
- **Future LLM Integration**: Designed for easy integration with OpenAI, local models, or Azure OpenAI

### API Interface

```python
# Initialize the conversation engine
conversation_engine = ConversationEngine(
    memory_service=memory_service,
    timeline_engine=timeline_engine,
    embedding_service=embedding_service
)

# Generate a response to a user query
response = conversation_engine.generate_response("What was your favorite family vacation?")

# Response structure
{
    'generated_answer': "I remember our trip to Hawaii in 2015...",
    'memories_used': ['mem_001', 'mem_045', 'mem_078'],
    'insights_used': ['Family vacations strengthen bonds', 'Taking time to relax is important'],
    'confidence_score': 0.87
}
```

### Workflow

1. **Semantic Search**: Finds top 5 most similar memories using vector embeddings
2. **Memory Retrieval**: Fetches full memory details for relevant memories
3. **Context Building**: Constructs chronological and thematic context from memories
4. **Insight Extraction**: Retrieves distilled wisdom and life lessons relevant to the query
5. **Prompt Construction**: Creates AI prompts with memory context, personality profile, and distilled insights
6. **Response Generation**: Generates conversational responses (currently placeholder)
7. **Confidence Calculation**: Computes response confidence based on similarity scores and insight quality

### Integration Points

- **MemoryCaptureService**: Retrieves stored memory objects
- **TimelineEngine**: Provides chronological organization and life stage grouping
- **MemoryEmbeddingService**: Performs semantic similarity search using vector embeddings
- **MemoryDistillationService**: Extracts wisdom, life lessons, and guidance from memories
- **PersonalityModelService**: Provides personality profiles for authentic responses

## Personality Modeling Engine

The Personality Modeling Engine analyzes stored memories to build comprehensive personality profiles that capture the authentic character, values, and behavioral patterns of the individual. This enables the Conversation Engine to generate responses that reflect the person's true personality.

### Key Features

- **Trait Analysis**: Identifies personality traits through keyword analysis and pattern recognition
- **Value Extraction**: Discovers core values and life principles from memory content
- **Communication Style Analysis**: Determines formality, emotional expression, and interaction patterns
- **Decision Pattern Recognition**: Identifies decision-making heuristics and approaches
- **Belief System Modeling**: Extracts core beliefs and philosophies from life experiences
- **Personality Evolution Tracking**: Analyzes how personality develops across life stages

### Personality Profile Structure

The engine generates structured personality profiles containing:

```python
@dataclass
class PersonalityProfile:
    traits: List[str]              # e.g., ['compassionate', 'adventurous', 'disciplined']
    core_beliefs: List[str]        # e.g., ['Family comes first', 'Honesty is crucial']
    communication_style: Dict      # formality, emotional_expression, directness
    values: List[str]              # e.g., ['family', 'integrity', 'achievement']
    decision_heuristics: List[str] # e.g., ['Makes decisions after careful consideration']
```

### API Interface

```python
# Initialize the personality modeling service
personality_service = PersonalityModelService(
    memory_service=memory_service,
    timeline_engine=timeline_engine,
    embedding_service=embedding_service
)

# Build a personality profile from all memories
profile = personality_service.build_personality_profile()

# Extract specific personality components
traits = personality_service.extract_traits(memories)
values = personality_service.extract_values(memories)
beliefs = personality_service.extract_core_beliefs(memories)
style = personality_service.extract_communication_style(memories)
patterns = personality_service.extract_decision_patterns(memories)

# Analyze personality evolution across life stages
evolution = personality_service.analyze_personality_evolution(memories)
```

### Integration with Conversation Engine

The Personality Modeling Engine seamlessly integrates with the Conversation Engine to provide personalized responses:

```python
# Create conversation engine with personality profile
conversation_engine = ConversationEngine(
    memory_service=memory_service,
    timeline_engine=timeline_engine,
    embedding_service=embedding_service,
    personality_profile=profile  # Enables personalized responses
)

# Generate personality-aware response
response = conversation_engine.generate_response("What do you think about taking risks?")
```

### Analysis Methods

- **Keyword Analysis**: Matches memory content against predefined trait and value dictionaries
- **Pattern Recognition**: Uses regex patterns to identify belief statements and decision patterns
- **Frequency Analysis**: Determines dominant traits based on occurrence frequency
- **Contextual Analysis**: Considers emotional metadata and relationship patterns
- **Temporal Analysis**: Tracks personality development across different life stages

### Future Enhancements

- **LLM Integration**: Use advanced language models for nuanced personality analysis
- **Semantic Clustering**: Group related personality indicators using embedding similarity
- **Cross-Memory Validation**: Ensure personality consistency across different memory types
- **Dynamic Profile Updates**: Adapt personality profiles as new memories are added

## Memory Distillation Engine

The Memory Distillation Engine analyzes stored memories to extract higher-level wisdom, life lessons, and guidance that transcend individual experiences. This enables the Conversation Engine to provide profound, insightful responses that reflect accumulated life wisdom rather than just surface-level memory recall.

### Key Features

- **Life Lesson Extraction**: Identifies valuable lessons learned from life experiences
- **Advice Generation**: Extracts practical advice and guidance from memory patterns
- **Pattern Recognition**: Discovers recurring themes and behavioral patterns across memories
- **Insight Categorization**: Organizes distilled wisdom by type (lessons, advice, regrets, principles)
- **Confidence Scoring**: Evaluates insight quality and reliability based on multiple factors
- **Personality Alignment**: Prioritizes insights that align with the individual's personality profile

### Distilled Insight Structure

The engine generates structured insights containing:

```python
@dataclass
class DistilledInsight:
    insight_type: str           # 'lesson', 'advice', 'regret', 'principle'
    insight_text: str           # The distilled wisdom text
    confidence_score: float     # 0-1 confidence in the insight
    source_memories: List[str]  # Memory IDs that contributed to this insight
    category: str              # Thematic category (e.g., 'family', 'career', 'relationships')
    emotional_intensity: float  # Emotional significance (0-1)
```

### API Interface

```python
# Initialize the memory distillation service
distillation_service = MemoryDistillationService(
    memory_service=memory_service,
    timeline_engine=timeline_engine,
    embedding_service=embedding_service,
    personality_profile=profile  # Optional for personality-aligned insights
)

# Extract different types of insights from memories
life_lessons = distillation_service.distill_life_lessons(memories)
advice = distillation_service.extract_advice(memories)
patterns = distillation_service.identify_recurring_patterns(memories)

# Categorize and organize insights
categorized_insights = distillation_service.categorize_insights(all_insights)

# Get insights relevant to a specific query
relevant_insights = distillation_service.get_relevant_insights("career advice", memories)
```

### Integration with Conversation Engine

The Memory Distillation Engine seamlessly integrates with the Conversation Engine to provide wisdom-based responses:

```python
# Create conversation engine with distillation service
conversation_engine = ConversationEngine(
    memory_service=memory_service,
    timeline_engine=timeline_engine,
    embedding_service=embedding_service,
    personality_profile=profile,
    distillation_service=distillation_service  # Enables wisdom-based responses
)

# Generate wisdom-enhanced response
response = conversation_engine.generate_response("What would you tell your younger self?")
# Response now includes distilled life lessons and advice
```

### Analysis Methods

- **Pattern Recognition**: Uses regex patterns to identify lesson statements, advice, and regrets
- **Frequency Analysis**: Determines insight importance based on occurrence across memories
- **Semantic Clustering**: Groups related insights using embedding similarity
- **Emotional Analysis**: Considers emotional metadata to gauge insight significance
- **Personality Alignment**: Filters insights to match the individual's personality profile
- **Confidence Scoring**: Multi-factor scoring based on keyword matches, emotional intensity, and source validation

### Future Enhancements

- **LLM Integration**: Use advanced language models for nuanced insight extraction and summarization
- **Cross-Memory Validation**: Ensure insight consistency across different memory types and time periods
- **Dynamic Insight Updates**: Adapt distilled wisdom as new memories are added
- **Multi-Language Support**: Extract insights from memories in different languages
- **Insight Evolution Tracking**: Analyze how wisdom develops and changes over time

## Legacy Access Control System

The Legacy Access Control System implements comprehensive privacy and security measures for the Legacy AI platform, ensuring that sensitive memories and personal information are only accessible to authorized beneficiaries under appropriate conditions. This system provides graduated access levels based on relationship, trust, and memory sensitivity.

### Key Features

- **Beneficiary Management**: Register and manage authorized users with different relationship types
- **Access Level Control**: Three-tier access system (Restricted, Limited, Full) based on relationship and trust
- **Memory Sensitivity Classification**: Tag memories with sensitivity levels (public, personal, medical, financial, intimate)
- **Legacy Activation Control**: Post-mortem access activation with verification mechanisms
- **Privacy-First Design**: Default to restrictive access with explicit permission grants

### Access Levels

- **RESTRICTED_ACCESS**: Basic public information and general memories
- **LIMITED_ACCESS**: Personal but non-sensitive memories and information
- **FULL_ACCESS**: Complete access including medical, financial, and intimate memories

### Relationship-Based Access

The system automatically assigns access levels based on beneficiary relationships:

- **Children & Spouse**: FULL_ACCESS by default
- **Parents**: LIMITED_ACCESS (respecting generational boundaries)
- **Siblings**: LIMITED_ACCESS
- **Friends & Others**: RESTRICTED_ACCESS

### API Interface

```python
# Initialize the access control service
access_service = LegacyAccessService()

# Register beneficiaries
access_service.register_beneficiary("child_123", Relationship.CHILD)
access_service.register_beneficiary("sibling_456", Relationship.SIBLING)

# Activate legacy access (after verification)
access_service.verify_legacy_activation("deceased")

# Check memory access authorization
memory_metadata = MemoryMetadata(
    memory_id="mem_001",
    sensitivity_tags=["personal", "medical"],
    created_date="2024-01-15",
    is_legacy_active=True
)

can_access = access_service.authorize_memory_access("child_123", memory_metadata)
access_level = access_service.get_access_level("child_123")
```

### Integration with Conversation Engine

The Legacy Access Control System integrates seamlessly with the Conversation Engine to filter memories based on user permissions:

```python
# Create conversation engine with access control
conversation_engine = ConversationEngine(
    memory_service=memory_service,
    timeline_engine=timeline_engine,
    embedding_service=embedding_service,
    personality_profile=profile,
    distillation_service=distillation_service,
    access_service=access_service  # Enables privacy protection
)

# Generate response with access filtering
response = conversation_engine.generate_response(
    "Tell me about your medical history",
    user_id="child_123"  # Access control applied
)

# Response includes access_denied flag if some memories were filtered
print(response['access_denied'])  # True if access was restricted
```

### Security Architecture

- **Multi-Factor Authorization**: Combines relationship, access level, and memory sensitivity
- **Audit Trail**: Logs all access attempts for compliance and security monitoring
- **Graceful Degradation**: System continues to function with partial access restrictions
- **Future Legal Integration**: Designed for integration with death certificates and legal verification services

### Future Enhancements

- **Legal Verification Integration**: Connect with government death registries and legal executor systems
- **Multi-Party Approval**: Require multiple beneficiaries for highly sensitive access
- **Time-Based Access**: Graduated access over time after legacy activation
- **Digital Estate Management**: Integration with broader digital estate planning platforms
- **Audit & Compliance**: Comprehensive logging for legal and regulatory requirements

## Response Moderation Service

The Response Moderation Service acts as a critical safety layer that reviews all AI-generated responses before they are returned to users. The Legacy AI platform deals with deeply personal and emotional content, making content moderation essential for maintaining trust, safety, and appropriateness.

### Key Features

- **Content Analysis**: Detects sensitive topics including violence, illegal activities, explicit content, and self-harm
- **Keyword Filtering**: Uses comprehensive keyword lists to identify inappropriate content
- **Pattern Recognition**: Employs regex patterns to detect harmful instructions and dangerous content
- **Safe Response Generation**: Automatically replaces inappropriate responses with safe alternatives
- **Emotional Intensity Monitoring**: Flags responses with excessive negative emotional language
- **Multi-Level Sensitivity Classification**: Categorizes content as safe, sensitive, inappropriate, or harmful

### Content Categories Monitored

- **Violence**: Physical harm, death, abuse, and related topics
- **Illegal Activity**: Crime, drugs, fraud, and unlawful behavior
- **Explicit Content**: Sexual topics, nudity, and inappropriate intimacy
- **Self-Harm**: Suicide, self-injury, and mental health crises
- **Hate Speech**: Discrimination, prejudice, and offensive language
- **Medical/Financial Sensitive**: Private health and money matters
- **Harmful Instructions**: Dangerous how-to content and illegal guidance

### API Interface

```python
# Initialize the response moderation service
moderation_service = ResponseModerationService()

# Review a response for appropriateness
review_result = moderation_service.review_response("Response text here")
# Returns: {'is_safe': bool, 'sensitivity_level': ContentSensitivity, 'issues_found': [...], 'recommended_action': str}

# Automatically adjust response if needed (primary method for ConversationEngine)
safe_response = moderation_service.adjust_response_if_needed("Potentially inappropriate response")
# Returns: Original response if safe, or safe alternative if inappropriate

# Detect sensitive content details
content_analysis = moderation_service.detect_sensitive_content("Response text")
# Returns: Detailed analysis of detected issues and severity levels
```

### Integration with Conversation Engine

The Response Moderation Service integrates seamlessly with the Conversation Engine to ensure all responses are safe:

```python
# Create conversation engine with response moderation
conversation_engine = ConversationEngine(
    memory_service=memory_service,
    timeline_engine=timeline_engine,
    embedding_service=embedding_service,
    personality_profile=profile,
    distillation_service=distillation_service,
    access_service=access_service,
    moderation_service=moderation_service  # Enables response safety
)

# Generate moderated response
response = conversation_engine.generate_response("Tell me about that violent incident")

# Response includes moderation metadata
print(response['moderation']['is_safe'])  # True if response passed moderation
print(response['generated_answer'])  # Safe response if original was inappropriate
```

### Moderation Architecture

- **Rule-Based Filtering**: Current implementation uses keyword detection and pattern matching
- **Severity Classification**: Issues are categorized by severity (low, medium, high)
- **Action Recommendations**: Suggests allow, modify, or block based on content analysis
- **Safe Response Templates**: Pre-written alternatives for different inappropriate content types
- **Context Preservation**: Maintains conversational flow while ensuring safety

### Future Enhancements

- **AI-Powered Moderation**: Integration with OpenAI Moderation API, Google Perspective API
- **Machine Learning Models**: Custom fine-tuned models for nuanced content analysis
- **Multi-Language Support**: Content moderation for responses in different languages
- **User Feedback Integration**: Learning from user reports to improve detection
- **Contextual Analysis**: Understanding intent and context beyond keyword matching
- **Real-Time Updates**: Dynamic keyword lists and pattern updates

## Upcoming Components

The following systems are planned for future development to enhance the Legacy AI platform:

- **Advanced NLP Processing**: Enhanced entity extraction and sentiment analysis for richer memory metadata
- **Multi-modal Memory Support**: Support for images, audio, and video memories alongside text
- **Collaborative Memory Curation**: Tools for family members to collaboratively review and enhance memories
- **AI-Powered Interview Adaptation**: Dynamic question generation based on previous responses and personality insights

## Testing

The Legacy AI platform includes comprehensive unit tests to ensure system reliability and behavior verification.

### Test Logging System

All unit tests generate human-readable summaries in `tests.log` located in the repository root. This log helps monitor AI system behavior and provides detailed test results for analysis.

#### Log Format

Each test entry includes:
- **Test Name**: Identifier for the test method
- **Timestamp**: When the test was executed
- **Input Parameters**: Parameters used in the test
- **Expected Result**: What the test expected
- **Actual Result**: What was actually returned
- **Status**: PASS or FAIL

Example log entry:
```
TEST: LegacyAccessService authorization
Timestamp: 2026-03-16 14:30:25
Input: user_role=child, memory_tag=sensitive
Expected: restricted
Actual: restricted
Status: PASS
---
```

#### Benefits of Test Logging

The `tests.log` file serves several important purposes:

1. **Behavior Monitoring**: Track how the AI system responds to different inputs over time
2. **Regression Detection**: Identify when system behavior changes unexpectedly
3. **Debugging Support**: Detailed input/output information for troubleshooting
4. **Compliance Verification**: Ensure AI responses meet safety and appropriateness standards
5. **Audit Trail**: Maintain a record of system testing for quality assurance

### Running Tests

```bash
# Run all tests (generates tests.log)
PYTHONPATH=backend python -m unittest discover -s backend/tests -p "test_*.py"

# Run specific test file
PYTHONPATH=backend python -m unittest backend.tests.test_legacy_access_service

# Run with verbose output
PYTHONPATH=backend python -m unittest discover -s backend/tests -p "test_*.py" -v

# View recent test results
tail -50 tests.log
```

### Test Coverage

- **Legacy Access Service**: Beneficiary registration, access level assignment, memory authorization
- **Response Moderation Service**: Content filtering, safe response generation, pattern detection

## Project Structure

### Directory Tree

```
.
|-- README.md
|-- tests.log
|-- ai
|   |-- data
|   |   `-- README.md
|   |-- models
|   |   `-- README.md
|   `-- scripts
|       `-- placeholder.py
|-- backend
|   |-- app
|   |   |-- api
|   |   |   |-- __init__.py
|   |   |   `-- family_interaction_api.py
|   |   |-- models
|   |   |   `-- __init__.py
|   |   `-- services
|   |       |-- ai
|   |       |   |-- conversation_engine.py
|   |       |   |-- __init__.py
|   |       |   |-- memory_distillation_service.py
|   |       |   `-- personality_model_service.py
|   |       |-- interview
|   |       |   |-- __init__.py
|   |       |   `-- structured_interview_service.py
|   |       |-- memory
|   |       |   |-- __init__.py
|   |       |   |-- memory_embedding_service.py
|   |       |   `-- vector_store.py
|   |       |-- security
|   |       |   |-- __init__.py
|   |       |   |-- legacy_access_service.py
|   |       |   `-- response_moderation_service.py
|   |       |-- media
|   |       |   |-- __init__.py
|   |       |   `-- media_memory_service.py
|   |       |-- __init__.py
|   |       |-- memory_capture_service.py
|   |-- tests
|   |   |-- __init__.py
|   |   |-- test_legacy_access_service.py
|   |   |-- test_response_moderation_service.py
|   |   `-- utils
|   |       `-- test_logger.py
```|   |       `-- timeline_engine.py
|   |-- config
|   |   `-- __init__.py
|   |-- tests
|   |   `-- test_placeholder.py
|   |-- app.py
|   `-- requirements.txt
|-- data
|   |-- memories
|   |   `-- README.md
|   `-- users
|       `-- README.md
|-- docs
|   `-- README.md
|-- frontend
|   |-- public
|   |   `-- index.html
|   |-- src
|   |   |-- components
|   |   |   `-- index.js
|   |   |-- pages
|   |   |   `-- index.js
|   |   `-- services
|   |       `-- index.js
|   |-- tests
|   |   `-- App.test.js
|   `-- package.json
|-- scripts
|   `-- README.md
|-- tests
|   `-- test_placeholder.py
`-- README.md

28 directories, 33 files
```

### Detailed Explanations

#### Root Level
- **README.md**: This file, containing project overview, setup instructions, and detailed structure explanations.

#### ai/
AI-related components and resources.
- **data/README.md**: Placeholder for AI training data directory. Explains the purpose and ensures the folder is tracked in Git.
- **models/README.md**: Placeholder for trained AI models. Includes notes on storing model artifacts and checkpoints.
- **scripts/placeholder.py**: Sample Python script for AI workflows, such as data preprocessing or model training.

#### backend/
Backend server code using Flask.
- **app.py**: Main Flask application file with routes for login, memories, and database setup.
- **requirements.txt**: Python dependencies for the backend.
- **app/api/__init__.py**: API endpoints module. Contains a sample health check route and setup for additional Blueprints.
- **app/api/family_interaction_api.py**: Family interaction API using FastAPI. Provides REST endpoints for asking questions to Legacy AI (/ask), browsing memories (/memories), exploring timelines (/timeline), and health checks. Integrates with ConversationEngine, LegacyAccessService, and ResponseModerationService for secure, moderated AI interactions.
- **app/models/__init__.py**: Data models module. Placeholder for SQLAlchemy models like User and Memory.
- **app/services/__init__.py**: Business logic services. Includes a sample service function for shared logic.
- **app/services/ai/__init__.py**: Package initializer for AI services, exporting ConversationEngine.
- **app/services/ai/conversation_engine.py**: Conversation engine for AI-powered interactions. Integrates memory capture, timeline, embedding, personality, distillation, and access control services to generate personalized responses to user queries based on stored memories, with placeholder for LLM integration.
- **app/services/ai/personality_model_service.py**: Personality modeling service. Analyzes memories to extract personality traits, beliefs, values, communication styles, and decision patterns, creating a comprehensive profile for authentic AI responses.
- **app/services/ai/memory_distillation_service.py**: Memory distillation service. Extracts higher-level wisdom from memories including life lessons, advice, regrets, and guiding principles, providing distilled insights for wisdom-based conversations.
- **app/services/interview/__init__.py**: Package initializer for interview services, exporting StructuredInterviewService.
- **app/services/interview/structured_interview_service.py**: Structured interview service. Guides users through systematic interviews across life domains (childhood, education, career, relationships, failures, lessons, advice, beliefs) to capture comprehensive life experiences. Automatically converts responses to memory entries with interview metadata, improving personality modeling and memory distillation quality.
- **app/services/memory_capture_service.py**: Memory capture service. Defines a Memory dataclass and MemoryCaptureService class for creating, updating, retrieving, and deleting memory entries with fields like title, description, timestamp, people_involved, location, emotions, and tags.
- **app/services/timeline_engine.py**: Timeline engine. Organizes memories chronologically, groups them by life stages (childhood, education, career, retirement), and allows querying by date range or life stage using birth date for age calculations.
- **app/services/memory/__init__.py**: Package initializer for memory services, exporting MemoryEmbeddingService and VectorStore.
- **app/services/memory/memory_embedding_service.py**: Semantic memory search service. Generates embeddings from memory text using a placeholder model, stores them in a vector store, and performs similarity search for retrieving relevant memories based on queries.
- **app/services/memory/vector_store.py**: Simple vector store implementation with cosine similarity search. Stores embeddings in JSON for persistence; designed to be replaced with scalable vector databases like Pinecone or Weaviate in production.
- **app/services/security/__init__.py**: Package initializer for security services, exporting LegacyAccessService and related enums.
- **app/services/security/legacy_access_service.py**: Legacy access control service. Manages posthumous access to memories with beneficiary registration, access levels (public, family, intimate), relationship verification, and authorization checks to ensure ethical memory sharing.
- **app/services/security/response_moderation_service.py**: Response moderation service. Reviews all AI-generated responses before delivery to ensure appropriateness, safety, and respectfulness. Detects sensitive topics (violence, illegal activity, explicit content, self-harm), applies content filtering, and replaces inappropriate responses with safe alternatives. Designed for future integration with external AI moderation APIs.
- **config/__init__.py**: Configuration helpers. Provides default config values for database and JWT.
- **tests/test_placeholder.py**: Placeholder test file for backend unit tests.

#### data/
Data storage directories.
- **memories/README.md**: Directory for stored memory data. Explains storing memory export files or fixtures.
- **users/README.md**: Directory for user data files. Notes on storing user JSON or serialized data.

#### docs/
Documentation directory.
- **README.md**: Placeholder for project documentation, including guides and architecture docs.

#### frontend/
Frontend web application using React.
- **package.json**: Node.js dependencies and scripts for the React app.
- **public/index.html**: Main HTML template for the React application.
- **src/components/index.js**: Placeholder for reusable UI components.
- **src/pages/index.js**: Placeholder for application pages, with a sample HomePage component.
- **src/services/index.js**: Placeholder for frontend services, with a sample service function.
- **tests/App.test.js**: Sample test for the main App component.

#### scripts/
Utility scripts.
- **README.md**: Explains the purpose of utility scripts for maintenance, data migration, etc.

#### tests/
General tests.
- **test_placeholder.py**: Placeholder test file for overall project tests.

This structure ensures all directories are tracked in Git by including at least one file in each. Update this README with each commit to reflect changes.

## Structured Interview Engine

The Structured Interview Engine is a core component of the Legacy AI platform that guides users through systematic, domain-specific interviews to capture comprehensive life experiences. This structured approach significantly enhances the quality and depth of the memory database, leading to more authentic AI personality modeling and richer wisdom distillation.

### Interview Categories

The service organizes questions across eight life domains:

- **Childhood**: Captures foundational memories and early influences
- **Education**: Documents learning experiences and academic journeys
- **Career**: Records professional achievements, challenges, and growth
- **Relationships**: Explores interpersonal connections and social dynamics
- **Failures and Regrets**: Extracts lessons from setbacks and mistakes
- **Life Lessons**: Identifies core principles and wisdom gained
- **Advice for Children**: Preserves guidance for future generations
- **Personal Beliefs**: Documents core values and life philosophy

### Memory Capture Pipeline Integration

The Structured Interview Engine seamlessly integrates with the memory capture pipeline:

1. **Question Presentation**: Users are guided through categorized question sets with follow-up prompts
2. **Response Recording**: Each response is stored with metadata about the question and category
3. **Automatic Memory Creation**: Responses are automatically converted to structured memory entries
4. **Metadata Tagging**: Memories are tagged with interview origin, category, and extracted entities
5. **Entity Extraction**: Simple NLP extracts people, locations, and emotions from responses
6. **AI Processing**: Tagged memories feed into personality modeling and distillation services

### Benefits for AI Modeling

- **Personality Modeling**: Consistent questions reveal communication patterns, values, and decision-making styles
- **Memory Distillation**: Targeted questions about regrets and lessons provide rich wisdom material
- **Data Quality**: Structured format ensures comprehensive coverage of important life domains
- **Authenticity**: Interview-derived memories provide deeper, more meaningful AI responses

### Usage Example

```python
from app.services.interview.structured_interview_service import StructuredInterviewService
from app.services.memory_capture_service import MemoryCaptureService

# Initialize services
memory_service = MemoryCaptureService()
interview_service = StructuredInterviewService(memory_service)

# Get available categories
categories = interview_service.get_interview_categories()

# Get questions for a category
questions = interview_service.get_questions_for_category("childhood")

# Record a response (automatically creates memory)
response_id = interview_service.record_interview_response(
    user_id="user123",
    question_id="childhood_001",
    response="My favorite childhood memory was building treehouses with my brother..."
)
```

## Media Memory Service

The Media Memory Service enables users to upload and manage multimedia memories including photos, audio recordings, and videos that are associated with structured memory entries. This service provides a foundation for rich, multimodal memory experiences that enhance the emotional impact and authenticity of Legacy AI interactions.

### Supported Media Types

- **Images**: JPG, PNG, GIF, BMP, TIFF, WebP (max 10MB)
- **Audio**: MP3, WAV, FLAC, AAC, OGG, M4A (max 50MB)
- **Video**: MP4, AVI, MOV, MKV, WMV, FLV, WebM (max 100MB)

### Integration with Memory Capture

The Media Memory Service is tightly integrated with the MemoryCaptureService to ensure data consistency:

1. **Memory-First Approach**: Media files can only be uploaded after a memory entry exists
2. **Metadata Linking**: Each media file is linked to a specific memory with rich metadata
3. **Access Control**: Media files inherit access controls from their associated memories
4. **Timeline Integration**: Media files appear in chronological timelines alongside text memories

### Cloud Storage Ready

The service is designed for seamless migration to cloud storage:

```python
# Current: Local file storage
media_service = MediaMemoryService(memory_service, "media_uploads")

# Future: Cloud storage integration
media_service.migrate_to_cloud_storage(s3_service)
```

### Usage Examples

```python
from app.services.media.media_memory_service import MediaMemoryService
from app.services.memory_capture_service import MemoryCaptureService

# Initialize services
memory_service = MemoryCaptureService()
media_service = MediaMemoryService(memory_service)

# Create a memory first
memory_id = memory_service.create_memory(
    title="Family Vacation 1995",
    description="Our wonderful trip to Hawaii with the whole family",
    tags=["vacation", "family", "hawaii"]
)

# Upload associated media
with open("family_photo.jpg", "rb") as f:
    media_id = media_service.upload_media(
        user_id="user123",
        memory_id=memory_id,
        file=f,
        filename="family_photo.jpg",
        description="Family photo at the beach"
    )

# List all media for a memory
media_files = media_service.list_media_for_memory(memory_id)

# Get media file path for serving
file_path = media_service.get_media_file_path(media_id)
```

### Benefits for Legacy AI

- **Emotional Depth**: Visual and audio memories create more immersive experiences
- **Memory Triggers**: Media files serve as powerful emotional and contextual cues
- **Authenticity**: Multimedia content provides richer, more authentic AI responses
- **Accessibility**: Supports various media formats for different user preferences
- **Scalability**: Cloud-ready architecture supports growing media collections

## Family Interaction API

The Family Interaction API provides REST endpoints that serve as the primary interface for beneficiaries and family members to interact with the Legacy AI system. This API integrates with the complete AI reasoning pipeline while enforcing access controls and response moderation.

### API Endpoints

- **POST /ask**: Submit questions to the Legacy AI and receive personalized responses
- **GET /timeline**: Retrieve chronologically organized life events and major milestones
- **GET /memories**: Browse authorized memories with optional category filtering and pagination
- **GET /health**: API health check and service status information

### Integration with AI Pipeline

The API serves as the entry point for user interactions, routing requests through the complete Legacy AI processing pipeline:

1. **User Query Reception**: Accepts natural language questions via POST /ask
2. **Conversation Engine Processing**: Routes queries through semantic search and response generation
3. **Access Control Enforcement**: Applies LegacyAccessService authorization for memory access
4. **Response Moderation**: Filters responses through ResponseModerationService for safety
5. **Structured Response Delivery**: Returns AI answers with metadata about memories used and confidence scores

### Authentication Design

The API is structured to easily accommodate future authentication:

```python
# Future authentication middleware can populate user_id from tokens
@app.middleware("http")
async def authenticate_user(request, call_next):
    # Extract user_id from JWT token or session
    user_id = extract_user_from_token(request.headers.get("Authorization"))
    request.state.user_id = user_id
    return await call_next(request)
```

### Usage Examples

```python
import requests

# Ask a question to Legacy AI
response = requests.post("http://localhost:8000/ask", json={
    "query": "What was your favorite family vacation?",
    "user_id": "child_beneficiary_123"
})

# Get timeline events
timeline = requests.get("http://localhost:8000/timeline", params={
    "user_id": "child_beneficiary_123",
    "limit": 20
})

# Browse memories
memories = requests.get("http://localhost:8000/memories", params={
    "user_id": "child_beneficiary_123",
    "category": "family",
    "limit": 10
})
```

### Response Formats

**Ask Response:**
```json
{
  "answer": "My favorite family vacation was our trip to Hawaii in 1995...",
  "memories_used": ["mem_001", "mem_045"],
  "insights_used": ["Travel brought our family closer together"],
  "confidence_score": 0.87,
  "access_denied": false,
  "moderation_applied": false,
  "timestamp": "2026-03-16T14:30:25Z"
}
```

**Timeline Response:**
```json
[
  {
    "id": "mem_001",
    "title": "First Day of School",
    "description": "Starting kindergarten at Lincoln Elementary...",
    "timestamp": "1965-09-01T00:00:00Z",
    "life_stage": "childhood",
    "age": 5
  }
]
```

## Conversation Engine

The Conversation Engine is the heart of the Legacy AI platform, enabling natural, personalized interactions between family members and the AI representation of their loved one. This sophisticated system orchestrates multiple AI services to generate contextually appropriate, emotionally resonant responses based on the deceased person's stored memories.

### Core Architecture

The Conversation Engine integrates multiple specialized services:

- **Memory Search**: Semantic similarity search using vector embeddings to find relevant memories
- **Access Control**: Filters memories based on beneficiary permissions and sensitivity levels
- **Context Building**: Constructs rich context from chronological, emotional, and relational data
- **Personality Integration**: Applies the person's communication style and values to responses
- **Wisdom Distillation**: Incorporates life lessons and distilled insights for meaningful guidance
- **Content Moderation**: Ensures all responses remain safe and appropriate

### Response Generation Workflow

1. **Query Processing**: Analyzes user questions for intent and emotional context
2. **Memory Retrieval**: Finds semantically similar memories using embedding similarity
3. **Authorization**: Applies access controls to filter accessible memories
4. **Context Enrichment**: Adds chronological context and life stage information
5. **Prompt Construction**: Builds detailed prompts incorporating personality and wisdom
6. **Response Generation**: Uses LLM integration (placeholder for OpenAI, local models, etc.)
7. **Safety Moderation**: Reviews and filters responses for appropriateness
8. **Response Delivery**: Returns moderated, personalized responses

### Integration Points

The Conversation Engine serves as the central orchestrator, connecting:

- **Memory Services**: Retrieval and embedding systems
- **AI Services**: Personality modeling and distillation
- **Security Services**: Access control and content moderation
- **Interview Services**: Structured data collection for improved responses

### Future LLM Integration

Currently uses placeholder response generation. Designed for integration with:

- **OpenAI GPT Models**: Advanced conversational AI with fine-tuning
- **Local LLMs**: Llama, Mistral, or other open-source models
- **Azure OpenAI**: Enterprise-grade AI services
- **Custom Fine-tuned Models**: Specialized for legacy interactions

### Usage Example

```python
from app.services.ai.conversation_engine import ConversationEngine
from app.services.memory_capture_service import MemoryCaptureService
from app.services.timeline_engine import TimelineEngine
from app.services.memory.memory_embedding_service import MemoryEmbeddingService
from app.services.security.legacy_access_service import LegacyAccessService
from app.services.security.response_moderation_service import ResponseModerationService

# Initialize all services
memory_service = MemoryCaptureService()
timeline_engine = TimelineEngine(memory_service)
embedding_service = MemoryEmbeddingService()
access_service = LegacyAccessService()
moderation_service = ResponseModerationService()

# Create conversation engine with all integrations
conversation_engine = ConversationEngine(
    memory_service=memory_service,
    timeline_engine=timeline_engine,
    embedding_service=embedding_service,
    access_service=access_service,
    moderation_service=moderation_service
)

# Generate personalized response
response = conversation_engine.generate_response(
    user_query="Tell me about Dad's childhood adventures",
    beneficiary=family_member
)
```

## Personality Model Service

The Personality Model Service analyzes stored memories to create a comprehensive psychological profile of the deceased person, enabling the AI to respond in a way that authentically reflects their personality, values, and communication style.

### Personality Analysis Framework

The service extracts multiple dimensions of personality:

- **Core Traits**: Extraversion, openness, conscientiousness, agreeableness, emotional stability
- **Communication Style**: Direct vs. indirect, formal vs. casual, emotional expression levels
- **Values & Beliefs**: Moral framework, life priorities, decision-making principles
- **Behavioral Patterns**: Problem-solving approaches, conflict resolution styles
- **Emotional Patterns**: How emotions are expressed and processed

### Memory Analysis Process

1. **Content Extraction**: Parses memory text for personality indicators
2. **Pattern Recognition**: Identifies recurring themes and behavioral patterns
3. **Trait Scoring**: Quantifies personality dimensions based on linguistic patterns
4. **Context Integration**: Considers life stage and situational factors
5. **Profile Synthesis**: Creates cohesive personality profile for AI responses

### Integration with Conversation Engine

The personality profile enhances AI responses by:

- **Authentic Voice**: Matching communication style and vocabulary
- **Value-Aligned Responses**: Reflecting the person's moral framework
- **Emotional Resonance**: Appropriate emotional expression levels
- **Behavioral Consistency**: Maintaining characteristic decision patterns

### Future Enhancements

Designed for integration with advanced personality analysis:

- **Psychological NLP Models**: Specialized models for personality trait detection
- **Multi-modal Analysis**: Voice recordings, writing samples, photos
- **Longitudinal Tracking**: Personality evolution across life stages
- **Cultural Context**: Culturally-aware personality interpretation

### Usage Example

```python
from app.services.ai.personality_model_service import PersonalityModelService
from app.services.memory_capture_service import MemoryCaptureService

# Initialize services
memory_service = MemoryCaptureService()
personality_service = PersonalityModelService()

# Analyze memories to build personality profile
memories = memory_service.list_memories()
personality_profile = personality_service.build_personality_profile(memories)

# Profile includes traits, values, communication style, etc.
print(f"Communication style: {personality_profile.communication_style}")
print(f"Core values: {personality_profile.values}")
```

## Memory Distillation Engine

The Memory Distillation Engine transforms raw memories into higher-level wisdom, extracting life lessons, advice, regrets, and guiding principles that provide deeper meaning and guidance for family members.

### Distillation Categories

The service identifies and extracts four types of distilled wisdom:

- **Life Lessons**: Fundamental principles learned through experience
- **Advice**: Practical guidance for future generations
- **Regrets**: Important lessons from mistakes and missed opportunities
- **Recurring Patterns**: Themes that appear across multiple life experiences

### Wisdom Extraction Process

1. **Pattern Recognition**: Identifies recurring themes across memories
2. **Lesson Extraction**: Distills explicit and implicit lessons from experiences
3. **Advice Synthesis**: Generates actionable guidance based on life experiences
4. **Regret Analysis**: Identifies important "what if" moments and their lessons
5. **Confidence Scoring**: Rates the significance and reliability of each insight

### Integration Benefits

Memory distillation enhances the AI's responses by providing:

- **Deeper Wisdom**: Beyond surface-level memories to fundamental life principles
- **Guidance Value**: Offers meaningful advice and life lessons
- **Emotional Support**: Helps family members process grief through shared wisdom
- **Legacy Preservation**: Captures the person's accumulated life experience

### Quality Assurance

The distillation process includes:

- **Confidence Scoring**: Each distilled insight has a confidence score
- **Source Attribution**: Links wisdom back to specific memories
- **Context Preservation**: Maintains situational context for insights
- **Bias Mitigation**: Balances positive and challenging experiences

### Future Enhancements

Prepared for advanced distillation techniques:

- **LLM-Powered Analysis**: Using large language models for deeper insight extraction
- **Sentiment Analysis**: Understanding emotional context of lessons
- **Cross-Memory Synthesis**: Connecting insights across different life domains
- **Personalized Wisdom**: Tailoring insights for specific family members

### Usage Example

```python
from app.services.ai.memory_distillation_service import MemoryDistillationService
from app.services.memory_capture_service import MemoryCaptureService

# Initialize services
memory_service = MemoryCaptureService()
distillation_service = MemoryDistillationService(memory_service)

# Extract wisdom from memories
memories = memory_service.list_memories()
life_lessons = distillation_service.distill_life_lessons(memories)
advice = distillation_service.extract_advice(memories)
regrets = distillation_service.extract_regrets(memories)
patterns = distillation_service.identify_recurring_patterns(memories)

# Each insight includes text, confidence score, and source memories
for lesson in life_lessons:
    print(f"Lesson: {lesson.insight_text} (Confidence: {lesson.confidence_score})")
```

## Legacy Access Control

The Legacy Access Control system provides ethical, posthumous access management for the Legacy AI platform, ensuring that sensitive memories are shared appropriately with designated family members while protecting privacy and maintaining trust.

### Access Control Framework

The system implements a hierarchical access model:

- **Public Level**: General memories suitable for all family and friends
- **Family Level**: Personal memories shared within the immediate family
- **Intimate Level**: Highly personal or sensitive memories for closest relationships

### Beneficiary Management

- **Registration Process**: Family members register with verified relationships
- **Relationship Verification**: Confirms familial connections and access levels
- **Authorization Checks**: Validates access permissions for each memory request
- **Audit Logging**: Tracks access patterns for security and compliance

### Memory Sensitivity Classification

Memories are automatically classified based on content analysis:

- **Content Analysis**: Scans for sensitive topics, personal information, emotional intensity
- **Context Evaluation**: Considers relationship context and emotional sensitivity
- **Dynamic Classification**: Access levels can be adjusted based on beneficiary feedback
- **Ethical Safeguards**: Prevents inappropriate access to highly personal content

### Integration with Conversation Engine

Access control is seamlessly integrated into the conversation pipeline:

1. **Query Analysis**: Determines appropriate access level for the conversation
2. **Memory Filtering**: Only authorized memories are included in responses
3. **Context Preservation**: Maintains conversation flow while respecting boundaries
4. **Transparent Operation**: Users unaware of filtered content for natural interaction

### Legal and Ethical Compliance

The system addresses important considerations:

- **Privacy Protection**: Respects individual privacy even after death
- **Family Dynamics**: Accommodates complex family relationships and boundaries
- **Cultural Sensitivity**: Adapts to different cultural norms around legacy sharing
- **Legal Compliance**: Designed to meet data protection and inheritance laws

### Future Enhancements

Prepared for advanced access control features:

- **Biometric Verification**: Voice or facial recognition for beneficiary authentication
- **Time-Based Access**: Gradual release of sensitive memories over time
- **Conditional Access**: Access based on life events or family agreements
- **Third-Party Auditing**: External verification of access control compliance

### Usage Example

```python
from app.services.security.legacy_access_service import LegacyAccessService, AccessLevel, Relationship
from app.services.memory_capture_service import MemoryCaptureService

# Initialize services
access_service = LegacyAccessService()
memory_service = MemoryCaptureService()

# Register a beneficiary
beneficiary = access_service.register_beneficiary(
    name="Sarah Johnson",
    relationship=Relationship.CHILD,
    access_level=AccessLevel.FAMILY
)

# Check memory access authorization
memory_id = "mem_001"
if access_service.authorize_memory_access(beneficiary, memory_id):
    memory = memory_service.retrieve_memory(memory_id)
    # Process authorized memory
else:
    # Handle unauthorized access
    pass
```

## Response Moderation Service

The Response Moderation Service is a critical safety component that ensures all AI-generated responses in the Legacy AI platform remain appropriate, respectful, and safe for family members. Given the deeply personal and emotional nature of legacy interactions, content moderation is essential to maintain trust and prevent harm.

### Safety Categories Monitored

The service monitors responses for multiple categories of inappropriate content:

- **Violence**: References to harm, injury, death, or aggressive behavior
- **Illegal Activity**: Discussions of crime, drugs, fraud, or unlawful actions
- **Explicit Content**: Sexual content, nudity, or inappropriate intimacy
- **Self-Harm**: References to suicide, self-injury, or severe emotional distress
- **Hate Speech**: Discriminatory language, prejudice, or harmful stereotypes
- **Medical Sensitivity**: Overly detailed medical information or diagnoses
- **Financial Privacy**: Personal financial details or sensitive monetary information

### Moderation Process

1. **Content Analysis**: Each response is scanned for sensitive keywords and patterns
2. **Pattern Detection**: Regex patterns identify potentially harmful instructions or content
3. **Severity Assessment**: Content is categorized by sensitivity level (safe, sensitive, inappropriate, harmful)
4. **Action Determination**: Based on severity, responses are allowed, modified, or blocked
5. **Safe Response Generation**: Inappropriate content is replaced with contextually appropriate alternatives

### Integration with Conversation Engine

The moderation service is seamlessly integrated into the conversation pipeline:

```
User Query → Memory Search → Context Building → Response Generation → Content Moderation → Safe Response
```

Every response passes through moderation before being returned to users, ensuring consistent safety standards.

### Future API Integration

The service is architected for easy integration with external moderation APIs:

- **OpenAI Moderation API**: Advanced content classification and safety scoring
- **Google Perspective API**: Toxicity and harassment detection
- **Custom ML Models**: Fine-tuned moderation models for legacy-specific content
- **Third-party Services**: Commercial content moderation platforms

### Safety Response Examples

When inappropriate content is detected, responses are replaced with safe alternatives:

- **Violence**: "I'm not able to discuss topics related to violence, but I'd be happy to share a peaceful memory from my life."
- **Illegal Activity**: "I can't discuss anything related to illegal activities. How about I share a story about following my principles?"
- **Self-Harm**: "If you're feeling distressed, please reach out to someone who can help you. I'm here to share positive memories and wisdom."
- **General Inappropriate**: "I'm not able to discuss that topic, but I'd be happy to share another meaningful memory."

### Usage Example

```python
from app.services.security.response_moderation_service import ResponseModerationService

# Initialize moderation service
moderation_service = ResponseModerationService()

# Review a response
review_result = moderation_service.review_response("Some potentially inappropriate response text")

if not review_result['is_safe']:
    safe_response = review_result['safe_alternative']
    print(f"Response moderated: {safe_response}")

# Or use the convenience method
safe_response = moderation_service.adjust_response_if_needed("original response")
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- Docker (optional)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ali919191/legacyai.git
   cd legacyai
   ```

2. Set up the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd ../frontend
   npm install
   ```

4. Configure the AI models:
   ```bash
   cd ../ai
   # Follow AI setup instructions
   ```

### Running the Application

1. Start the backend server:
   ```bash
   cd backend
   python app.py
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm start
   ```

## Contributing

Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
