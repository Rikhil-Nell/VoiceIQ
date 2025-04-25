# VoiceIQ

**VoiceIQ** is an intelligent call log processing system designed to handle customer support interactions efficiently. It leverages advanced AI models and APIs to transcribe, analyze, and store call logs while ensuring sensitive information is sanitized and securely managed. This project is built for enterprise use and integrates seamlessly with external APIs and databases.

---

## 🚀 Features

- **🎙 Audio Transcription**  
  Converts audio files (`.wav` or `.mp3`) into text using external transcription APIs and Groq's Whisper API.

- **🛡️ Data Sanitization**  
  Automatically masks sensitive information such as credit card numbers and SSNs in transcripts.

- **🧠 AI-Powered Analysis**
  - **Call Log Agent**: Formats and structures raw transcripts into a readable format.
  - **Report Agent**: Extracts key details from transcripts and generates structured reports.
  - **Database Agent**: Extracts actionable insights and stores them in a database.
  - **Chat Agent**: Provides conversational insights and follow-up recommendations based on call logs.

- **📦 Database Management**
  - Create, retrieve, update, and delete call logs in a Supabase database.
  - Query specific columns or retrieve all logs with a limit.

- **🌐 FastAPI Integration**
  Provides a RESTful API for uploading call logs, querying data, and managing logs.

- **🔐 Environment Configuration**
  Securely manages API keys and other sensitive settings using `.env` files.

---

## 📦 Installation & Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-company/voiceIQ.git
   cd voiceIQ
   ```

2. **Set up a Python virtual environment (using pip)**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up your environment variables**:
   - Create a `.env` file in the project root.
   - Refer to `settings.py` for required fields. All fields are explicitly defined in the Settings class.
   - You can override values with environment variables directly (e.g., via Docker or CI/CD pipelines).
  
4. **Python version**:
   - This project is tested with Python 3.13 (see `.python-version`).

## 🚦 Usage

### ✅ Running the API Server

Start the FastAPI server:

```bash
uvicorn app:app --reload
```

The API will be available at:
📍 [http://127.0.0.1:8000]

### 🧪 API Endpoints

#### 🎧 Upload Call Log

- **Endpoint**: `POST /create_log`
- **Description**: Upload an audio file (`.wav` or `.mp3`) to transcribe, analyze, and store in the database.

#### 📂 Get All Logs

- **Endpoint**: `GET /logs/all/{limit}`
- **Description**: Retrieve all call logs with a specified limit.

#### 🧩 Get Specific Columns

- **Endpoint**: `POST /logs/columns`
- **Description**: Retrieve specific columns from the database with a limit.

#### 📝 Get Report

- **Endpoint**: `POST /logs/report`
- **Description**: Retrieve a structured report for a specific call log by UUID.

#### 💬 Chat with Call Insights

- **Endpoint**: `POST /chat`
- **Description**: Interact with the system to get conversational insights or follow-up recommendations based on call logs.

### 📈 Example Workflow

1. Upload a call log using the `/create_log` endpoint.
2. The system transcribes the audio, sanitizes sensitive data, and processes it using AI agents.
3. The processed data is stored in the database.
4. Retrieve or analyze it via available endpoints or interact with the chat agent for insights.

## 🗂 Project Structure

```sh
voiceIQ/
├── main.py              # Orchestrates transcription, analysis, and storage
├── app.py               # FastAPI endpoints
├── transcription.py     # Audio transcription and sanitization
├── database.py          # Database operations with Supabase
├── agents.py            # AI agents for processing
├── memory.py            # Handles user memory for chat interactions
├── settings.py          # Environment configuration
├── prompts/             # Prompt templates for agents
├── .env                 # Your environment variables (not committed)
├── README.md            # This file
├── requirements.txt     # Dependencies
├── Dockerfile           # Docker configuration
└── pyproject.toml       # Project metadata
```

## 📝 License

This project is licensed under the MIT License.
See the LICENSE file for details.
