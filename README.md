# Legacy AI Platform

Legacy AI is a platform designed to capture and preserve life experiences as structured memories, enabling family members to interact with an AI representation of their loved one after they pass away.

## Features

- **Life Experience Capture**: Tools and interfaces to record personal stories, memories, and experiences.
- **Structured Memory Storage**: Organize and store memories in a structured format for AI processing.
- **AI Interaction**: Allow family members to converse with an AI-powered persona based on the stored memories.
- **Secure Access**: Posthumous access controls for designated family members.

## Project Structure

### Directory Tree

```
.
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
|   |   |   `-- __init__.py
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
|   |       |-- __init__.py
|   |       |-- memory_capture_service.py
|   |       `-- timeline_engine.py
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

27 directories, 31 files
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
