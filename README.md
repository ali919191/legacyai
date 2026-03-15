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
|   |       |-- __init__.py
|   |       `-- memory_capture_service.py
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

25 directories, 22 files
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
- **app/services/memory_capture_service.py**: Memory capture service. Defines a Memory dataclass and MemoryCaptureService class for creating, updating, retrieving, and deleting memory entries with fields like title, description, timestamp, people_involved, location, emotions, and tags.
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
