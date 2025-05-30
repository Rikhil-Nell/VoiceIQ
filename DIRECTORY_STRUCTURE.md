# Directory structure

VoiceIQ/
├── .env                        # Environment variables (not in repo)
├── .gitignore                  # Git ignore rules
├── .python-version             # Python version pin
├── Dockerfile                  # Docker build instructions (not shown, assumed present)
├── LICENSE                     # Project license (GPLv3)
├── README.md                   # Project overview and instructions (not shown, assumed present)
├── requirements.txt            # Python dependencies
├── uv.lock                     # Lock file for dependencies
├── app.py                      # (Not present, assumed main entry if exists)
├── agents.py                   # (Not present, assumed for agent logic if exists)
├── auth.py                     # JWT authentication and password hashing helpers
├── database.py                 # (Not present, assumed for DB logic if exists)
├── main.py                     # (Not present, assumed main entry if exists)
├── memory.py                   # Handles user chat memory with Supabase
├── santization.py              # Service for PII redaction using regex and LLM
├── settings.py                 # Loads and parses environment/configuration variables
├── transcription.py            # Audio transcription logic (local API and Groq Whisper)
├── prompts/
│   ├── call_log_agent_prompt.txt      # Prompt for formatting call logs by speaker
│   ├── chat_agent_prompt.txt          # Prompt for chat agent to answer questions about calls
│   ├── database_agent_prompt.txt      # Prompt for extracting structured info for database
│   └── report_agent_prompt.txt        # Prompt for generating a structured customer support report
├── .github/
│   └── workflows/
│       └── deploy.yaml         # GitHub Actions workflow for Docker build and deploy
└── scripts/                    # (Not present, suggested for utility scripts)

Brief for each file:

- .env: Stores environment variables (API keys, secrets, etc.), not checked into version control.
- .gitignore: Specifies files and folders to be ignored by git.
- .python-version: Specifies the Python version for the project (3.13).
- Dockerfile: Instructions for building the Docker image (not shown, assumed present).
- LICENSE: GPLv3 license for the project.
- requirements.txt: Lists all Python dependencies for the project.
- uv.lock: Lock file for reproducible Python dependency installs.
- auth.py: Contains JWT authentication helpers and password hashing/verification logic.
- memory.py: Implements chat memory storage and retrieval using Supabase.
- santization.py: Provides a service to redact PII from transcripts using regex and LLM.
- settings.py: Loads and parses environment variables, including GCP credentials, using Pydantic.
- transcription.py: Handles audio transcription via external API and Groq Whisper model.
- prompts/: Contains prompt templates for various LLM agents (call log formatting, chat, database extraction, report generation).
- .github/workflows/deploy.yaml: CI/CD workflow for building and deploying the Docker image.
