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
|   |       |   `-- legacy_access_service.py
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
